"""SQLite persistence for the paper-mode scanner."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mint TEXT NOT NULL UNIQUE,
    name TEXT,
    symbol TEXT,
    uri TEXT,
    creator TEXT,
    signature TEXT,
    market_cap_sol REAL,
    initial_buy_sol REAL,
    tokens_in_pool REAL,
    pool TEXT,
    source TEXT,
    detected_at_utc TEXT NOT NULL,
    rugcheck_score INTEGER,
    rugcheck_score_norm REAL,
    rugcheck_risks TEXT,
    rugcheck_checked_at_utc TEXT,
    flagged INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signature TEXT,
    mint TEXT,
    source TEXT NOT NULL,
    detected_at_utc TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_detections_signature ON detections(signature);
CREATE INDEX IF NOT EXISTS idx_detections_source ON detections(source);
"""


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def upsert_token(conn: sqlite3.Connection, token: dict) -> None:
    conn.execute(
        """
        INSERT INTO tokens (
            mint, name, symbol, uri, creator, signature, market_cap_sol,
            initial_buy_sol, tokens_in_pool, pool, source, detected_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(mint) DO UPDATE SET
            name = COALESCE(excluded.name, name),
            symbol = COALESCE(excluded.symbol, symbol),
            uri = COALESCE(excluded.uri, uri),
            market_cap_sol = COALESCE(excluded.market_cap_sol, market_cap_sol),
            initial_buy_sol = COALESCE(excluded.initial_buy_sol, initial_buy_sol),
            tokens_in_pool = COALESCE(excluded.tokens_in_pool, tokens_in_pool)
        """,
        (
            token.get("mint"),
            token.get("name"),
            token.get("symbol"),
            token.get("uri"),
            token.get("creator"),
            token.get("signature"),
            token.get("market_cap_sol"),
            token.get("initial_buy_sol"),
            token.get("tokens_in_pool"),
            token.get("pool"),
            token.get("source", "pumpportal"),
            token.get("detected_at_utc"),
        ),
    )
    conn.commit()


def record_detection(conn: sqlite3.Connection, source: str, signature: str | None, mint: str | None, now_utc: str) -> None:
    conn.execute(
        "INSERT INTO detections (signature, mint, source, detected_at_utc) VALUES (?, ?, ?, ?)",
        (signature, mint, source, now_utc),
    )
    conn.commit()


def save_rugcheck(conn: sqlite3.Connection, mint: str, summary: dict | None, flagged: bool, now_utc: str) -> None:
    import json

    if summary is None:
        return
    risks = [
        {"name": r.get("name"), "level": r.get("level"), "description": r.get("description", "")[:200]}
        for r in (summary.get("risks") or [])
    ]
    conn.execute(
        """
        UPDATE tokens
        SET rugcheck_score = ?, rugcheck_score_norm = ?, rugcheck_risks = ?,
            rugcheck_checked_at_utc = ?, flagged = ?
        WHERE mint = ?
        """,
        (
            summary.get("score"),
            summary.get("score_normalised"),
            json.dumps(risks, ensure_ascii=False),
            now_utc,
            int(flagged),
            mint,
        ),
    )
    conn.commit()
