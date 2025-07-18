from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timedelta


def gc(db_path: str, days: int) -> None:
    conn = sqlite3.connect(db_path)
    cutoff = datetime.utcnow() - timedelta(days=days)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS agent_states (
        agent_id TEXT PRIMARY KEY,
        status TEXT,
        retry_count INTEGER,
        updated_at REAL
    )"""
    )
    conn.execute(
        "DELETE FROM agent_states WHERE updated_at < ?",
        (cutoff.timestamp(),),
    )
    conn.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Garbage collect old state")
    parser.add_argument("db", help="Path to sqlite db")
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()
    gc(args.db, args.days)
