from __future__ import annotations

import re
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Callable

from .memory_hub import MemoryHub
from .schemas import StateCheckpoint


def redact(text: str) -> str:
    """Redact simple personal data like email addresses."""
    return re.sub(r"[\w.-]+@[\w.-]+", "[redacted]", text)


@dataclass
class Agent:
    """Lightweight agent representation."""

    name: str
    run_fn: Callable[[Any], str]
    memory: dict[str, Any]

    def run(self, inp: Any) -> str:
        return self.run_fn(inp)


def build_micro_agent(name: str, tool_fn: Callable[[Any], str], hub: MemoryHub) -> Agent:
    return Agent(name=name, run_fn=tool_fn, memory={"redis": hub.redis})


def build_taskmaster(name: str, run_fn: Callable[[Any], str], hub: MemoryHub) -> Agent:
    return Agent(name=name, run_fn=run_fn, memory={"redis": hub.redis, "pg": hub.pg})


def build_head(name: str, run_fn: Callable[[Any], str], hub: MemoryHub) -> Agent:
    def guarded(inp: Any) -> str:
        output = run_fn(inp)
        return redact(output)

    return Agent(
        name=name,
        run_fn=guarded,
        memory={"redis": hub.redis, "pg": hub.pg, "vec": hub.vec, "obj": hub.obj},
    )


def build_c_level(name: str, run_fn: Callable[[Any], str], hub: MemoryHub) -> Agent:
    def metered(inp: Any) -> str:
        start = time.time()
        result = run_fn(inp)
        duration = time.time() - start
        hub.pg.execute("CREATE TABLE IF NOT EXISTS budget_ledger (name TEXT, seconds REAL)")
        hub.pg.execute("INSERT INTO budget_ledger (name, seconds) VALUES (?, ?)", (name, duration))
        hub.pg.commit()
        return result

    return Agent(name=name, run_fn=metered, memory={"pg": hub.pg, "kafka": hub.kafka})


# Persistence helpers


def save_checkpoint(conn: sqlite3.Connection, cp: StateCheckpoint) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS agent_states (
        agent_id TEXT PRIMARY KEY,
        status TEXT,
        retry_count INTEGER,
        updated_at REAL
    )"""
    )
    conn.execute(
        "INSERT OR REPLACE INTO agent_states VALUES (?, ?, ?, ?)",
        (cp.agent_id, cp.status, cp.retry_count, time.time()),
    )
    conn.commit()


def load_checkpoint(conn: sqlite3.Connection, agent_id: str) -> StateCheckpoint | None:
    cur = conn.execute(
        "SELECT agent_id, status, retry_count FROM agent_states WHERE agent_id=?", (agent_id,)
    )
    row = cur.fetchone()
    if row:
        return StateCheckpoint(agent_id=row[0], status=row[1], retry_count=row[2])
    return None


def record_retry(conn: sqlite3.Connection, agent_id: str) -> int:
    cp = load_checkpoint(conn, agent_id)
    if cp is None:
        cp = StateCheckpoint(agent_id=agent_id, status="retry", retry_count=1)
    else:
        cp.retry_count += 1
        cp.status = "retry"
    save_checkpoint(conn, cp)
    return cp.retry_count
