"""Paper-mode scanner entry point.

Listens for new pump.fun tokens (PumpPortal, plus an optional Helius
logsSubscribe feed for latency comparison), checks them with RugCheck and
stores everything in SQLite. It never signs or sends transactions.

Usage:
    python -m scanner                 # run until Ctrl-C
    python -m scanner --duration 60   # bounded run (for tests)
    python -m scanner --db data/x.sqlite3
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone

import websockets

from scanner.config import HELIUS_WSS_TEMPLATE, PUMP_PROGRAM_ID, ScannerConfig
from scanner.db import connect, record_detection, save_rugcheck, upsert_token
from scanner.rugcheck import RugCheckClient

log = logging.getLogger("scanner")

WS_MAX_MESSAGE_BYTES = 32 * 1024 * 1024


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def feed_label(url: str) -> str:
    """scheme://host/path — never log query strings (they carry API keys)."""
    from urllib.parse import urlsplit

    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}{parts.path}"


def clock() -> str:
    return datetime.now().strftime("%H:%M:%S")


class AppState:
    def __init__(self, cfg: ScannerConfig) -> None:
        self.cfg = cfg
        self.conn = connect(cfg.db_path)
        self.rugcheck = RugCheckClient(cfg.rugcheck_base, cfg.rugcheck_timeout_s, cfg.rugcheck_concurrency)
        self.seen: set[str] = set()
        self.rugcheck_attempts: dict[str, int] = {}
        self.pp_count = 0
        self.helius_count = 0


def _creation_like(evt: dict) -> bool:
    """PumpPortal creation events may omit name/symbol; trades carry user-side
    fields we don't need. We record the first sighting of any mint either way."""
    return bool(evt.get("name") or evt.get("uri") or evt.get("initialBuy") is not None)


async def handle_pumpportal(state: AppState, evt: dict) -> None:
    mint = evt.get("mint")
    if not mint:
        return
    state.pp_count += 1
    ts = now_utc()
    record_detection(state.conn, "pumpportal", evt.get("signature"), mint, ts)
    if mint in state.seen or not _creation_like(evt):
        return
    state.seen.add(mint)
    upsert_token(state.conn, {
        "mint": mint,
        "name": evt.get("name"),
        "symbol": evt.get("symbol"),
        "uri": evt.get("uri"),
        "creator": evt.get("creator"),
        "signature": evt.get("signature"),
        "market_cap_sol": evt.get("marketCapSol"),
        "initial_buy_sol": evt.get("initialBuy"),
        "tokens_in_pool": evt.get("tokensInPool"),
        "pool": evt.get("pool"),
        "source": "pumpportal",
        "detected_at_utc": ts,
    })
    asyncio.create_task(check_and_store_rugcheck(state, mint))
    print(f"[{clock()}] NEW  {mint}  {evt.get('symbol') or evt.get('name') or '-'}"
          f"  mcap={evt.get('marketCapSol') or '-'}")


async def check_and_store_rugcheck(state: AppState, mint: str) -> None:
    summary = await state.rugcheck.summary(mint)
    flagged = state.rugcheck.is_flagged(summary, state.cfg.rugcheck_max_score_norm)
    save_rugcheck(state.conn, mint, summary, flagged, now_utc())
    if summary is not None:
        mark = "!! FLAG" if flagged else f"ok   score={summary.get('score_normalised')}"
        print(f"[{clock()}]      rugcheck {mint[:8]}… {mark}")
    else:
        print(f"[{clock()}]      rugcheck {mint[:8]}… unavailable")


async def recheck_loop(state: AppState) -> None:
    """RugCheck takes a while to index brand-new mints; periodically retry
    the ones still unchecked, giving up after recheck_max_attempts tries."""
    cfg = state.cfg
    while True:
        await asyncio.sleep(cfg.recheck_interval_s)
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(seconds=cfg.recheck_min_age_s)).isoformat(timespec="milliseconds")
            rows = state.conn.execute(
                "SELECT mint FROM tokens WHERE rugcheck_score IS NULL AND detected_at_utc <= ?",
                (cutoff,),
            ).fetchall()
            due = [r["mint"] for r in rows if state.rugcheck_attempts.get(r["mint"], 0) < cfg.recheck_max_attempts]
            log.info("rugcheck recheck: %d/%d due", len(due), len(rows))
            for mint in due:
                state.rugcheck_attempts[mint] = state.rugcheck_attempts.get(mint, 0) + 1
                asyncio.create_task(check_and_store_rugcheck(state, mint))
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("recheck loop error")


async def handle_helius(state: AppState, msg: dict) -> None:
    value = (msg.get("params") or {}).get("result", {}).get("value") or {}
    logs = value.get("logs") or []
    if not any("Instruction: Create" in line for line in logs):
        return
    state.helius_count += 1
    record_detection(state.conn, "helius-logs", value.get("signature"), None, now_utc())


async def ws_loop(state: AppState, url: str, subscribe_msgs: list[dict], handler) -> None:
    delay = state.cfg.reconnect_min_s
    while True:
        try:
            async with websockets.connect(url, max_size=WS_MAX_MESSAGE_BYTES) as ws:
                for m in subscribe_msgs:
                    await ws.send(json.dumps(m))
                log.info("connected: %s", feed_label(url))
                delay = state.cfg.reconnect_min_s
                async for raw in ws:
                    try:
                        await handler(state, json.loads(raw))
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        # one bad event must never kill the connection
                        log.exception("handler error")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.warning("ws %s dropped (%s) — reconnecting in %.0fs", feed_label(url), exc, delay)
        await asyncio.sleep(delay)
        delay = min(delay * 2, state.cfg.reconnect_max_s)


async def run(duration: float | None) -> None:
    cfg = ScannerConfig.load()
    state = AppState(cfg)
    print(f"scanner: db={cfg.db_path}  pumpportal=on  helius={'on' if cfg.helius_wss else 'off'}"
          f"  rugcheck_max_score_norm={cfg.rugcheck_max_score_norm}")
    tasks = [
        asyncio.create_task(ws_loop(
            state, cfg.pumpportal_ws,
            [{"method": "subscribeNewToken"}], handle_pumpportal,
        )),
    ]
    if cfg.helius_wss:
        tasks.append(asyncio.create_task(ws_loop(
            state, cfg.helius_wss,
            [{"jsonrpc": "2.0", "id": 1, "method": "logsSubscribe",
              "params": [{"mentions": [PUMP_PROGRAM_ID]}]}],
            handle_helius,
        )))
    tasks.append(asyncio.create_task(recheck_loop(state)))
    try:
        if duration:
            await asyncio.sleep(duration)
        else:
            await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await state.rugcheck.close()
        state.conn.close()
        print(f"scanner stopped: tokens_seen={len(state.seen)} "
              f"pumpportal_events={state.pp_count} helius_creates={state.helius_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="paper-mode pump.fun token scanner")
    parser.add_argument("--duration", type=float, default=None, help="stop after N seconds (default: run forever)")
    parser.add_argument("--db", default=None, help="override sqlite path")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        asyncio.run(run(args.duration))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
