import sqlite3

import fakeredis

from agents.department import (
    KafkaProducer,
    MemoryHub,
    ObjectStorageClient,
    StateCheckpoint,
    VectorStoreDAO,
    build_c_level,
    build_head,
    build_micro_agent,
    build_taskmaster,
    load_checkpoint,
    record_retry,
    save_checkpoint,
)


def make_hub() -> MemoryHub:
    redis = fakeredis.FakeRedis()
    pg = sqlite3.connect(":memory:")
    return MemoryHub(redis, pg, VectorStoreDAO(), ObjectStorageClient(), KafkaProducer())


def test_memory_injection() -> None:
    hub = make_hub()

    micro = build_micro_agent("m", lambda x: "ok", hub)
    assert list(micro.memory) == ["redis"]

    task = build_taskmaster("t", lambda x: "ok", hub)
    assert set(task.memory) == {"redis", "pg"}

    head = build_head("h", lambda x: "user@example.com", hub)
    assert set(head.memory) == {"redis", "pg", "vec", "obj"}
    assert head.run(None) == "[redacted]"

    c = build_c_level("c", lambda x: "done", hub)
    assert set(c.memory) == {"pg", "kafka"}
    res = c.run(None)
    assert res == "done"


def test_state_retry() -> None:
    hub = make_hub()
    cp = StateCheckpoint(agent_id="a1", status="pending", retry_count=0)
    save_checkpoint(hub.pg, cp)
    assert load_checkpoint(hub.pg, "a1") == cp
    assert record_retry(hub.pg, "a1") == 1
    assert record_retry(hub.pg, "a1") == 2
