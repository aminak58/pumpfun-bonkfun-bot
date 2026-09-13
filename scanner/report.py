"""Quick stats over the scanner database.

Usage: python -m scanner.report [--db data/scanner.sqlite3]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/scanner.sqlite3")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    total = conn.execute("SELECT COUNT(*) c FROM tokens").fetchone()["c"]
    checked = conn.execute("SELECT COUNT(*) c FROM tokens WHERE rugcheck_score IS NOT NULL").fetchone()["c"]
    flagged = conn.execute("SELECT COUNT(*) c FROM tokens WHERE flagged = 1").fetchone()["c"]
    print(f"tokens: {total}   rugcheck-checked: {checked} ({100 * checked / total:.0f}%)" if total else "tokens: 0")
    if checked:
        print(f"flagged: {flagged} ({100 * flagged / checked:.0f}% of checked)")

    print("\n-- per day (UTC) --")
    for row in conn.execute(
        "SELECT substr(detected_at_utc, 1, 10) day, COUNT(*) c FROM tokens GROUP BY day ORDER BY day DESC LIMIT 7"
    ):
        print(f"  {row['day']}: {row['c']}")

    print("\n-- detections per source --")
    for row in conn.execute("SELECT source, COUNT(*) c FROM detections GROUP BY source"):
        print(f"  {row['source']}: {row['c']}")

    print("\n-- feed latency comparison (same signature, helius minus pumpportal) --")
    rows = conn.execute(
        """
        SELECT a.detected_at_utc pp_ts, b.detected_at_utc h_ts FROM detections a
        JOIN detections b ON a.signature = b.signature
        WHERE a.source='pumpportal' AND b.source='helius-logs'
        """
    ).fetchall()
    if rows:
        from datetime import datetime

        deltas = []
        for r in rows:
            pp = datetime.fromisoformat(r["pp_ts"])
            h = datetime.fromisoformat(r["h_ts"])
            deltas.append((h - pp).total_seconds() * 1000)
        deltas.sort()
        mid = deltas[len(deltas) // 2]
        avg = sum(deltas) / len(deltas)
        print(f"  n={len(deltas)}  avg={avg:.0f}ms  median={mid:.0f}ms  "
              f"min={deltas[0]:.0f}ms  max={deltas[-1]:.0f}ms  (negative = helius first)")
    else:
        print("  no overlapping signatures yet")

    print("\n-- top rugcheck risks --")
    counter: Counter = Counter()
    for (raw,) in conn.execute("SELECT rugcheck_risks FROM tokens WHERE rugcheck_risks IS NOT NULL"):
        for risk in json.loads(raw):
            counter[f"{risk.get('level')}/{risk.get('name')}"] += 1
    for name, count in counter.most_common(8):
        print(f"  {count:5d}  {name}")

    conn.close()


if __name__ == "__main__":
    main()
