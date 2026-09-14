"""Scanner configuration, loaded from environment (.env supported).

Paper-mode scanner: detects new pump.fun tokens, checks them with RugCheck,
and stores everything in SQLite. It never signs or sends transactions.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

PUMP_PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

HELIUS_WSS_TEMPLATE = "wss://mainnet.helius-rpc.com/?api-key={api_key}"


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass
class ScannerConfig:
    pumpportal_ws: str
    helius_wss: str | None
    rugcheck_base: str
    db_path: str
    rugcheck_max_score_norm: float
    rugcheck_concurrency: int
    rugcheck_timeout_s: float
    reconnect_min_s: float
    reconnect_max_s: float
    recheck_interval_s: float
    recheck_min_age_s: float
    recheck_max_attempts: int

    @classmethod
    def load(cls) -> "ScannerConfig":
        load_dotenv(override=True)
        helius_key = _env("HELIUS_API_KEY")
        wss_override = _env("SOLANA_NODE_WSS_ENDPOINT")
        helius_wss = wss_override or (HELIUS_WSS_TEMPLATE.format(api_key=helius_key) if helius_key else None)
        return cls(
            pumpportal_ws=_env("PUMPPORTAL_WS_URL", "wss://pumpportal.fun/api/data"),
            helius_wss=helius_wss or None,
            rugcheck_base=_env("RUGCHECK_BASE_URL", "https://api.rugcheck.xyz/v1"),
            db_path=_env("SCANNER_DB_PATH", "data/scanner.sqlite3"),
            rugcheck_max_score_norm=float(_env("RUGCHECK_MAX_SCORE_NORM", "60")),
            rugcheck_concurrency=int(_env("RUGCHECK_CONCURRENCY", "4")),
            rugcheck_timeout_s=float(_env("RUGCHECK_TIMEOUT_S", "10")),
            reconnect_min_s=float(_env("RECONNECT_MIN_S", "2")),
            reconnect_max_s=float(_env("RECONNECT_MAX_S", "60")),
            recheck_interval_s=float(_env("RECHECK_INTERVAL_S", "600")),
            recheck_min_age_s=float(_env("RECHECK_MIN_AGE_S", "300")),
            recheck_max_attempts=int(_env("RECHECK_MAX_ATTEMPTS", "5")),
        )
