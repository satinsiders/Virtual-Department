# Virtual department memory guide

This guide demonstrates connecting a hierarchy of agents to durable data
stores with a small dependency‑injection container.

## Storage tiers

Information flows through several tiers of durability:

1. **Context window** — transient, per model call.
2. **Redis** — short‑lived cache used for minutes.
3. **PostgreSQL** — drafts, status flags and checkpoints stored for days.
4. **Vector database and object storage** — final artifacts and embeddings for long‑term storage.
5. **Kafka** — append‑only audit log for the lifetime of the account.

Each agent layer only interacts with the storage systems it needs.
A micro agent only touches Redis, taskmasters read Redis and write to
PostgreSQL, heads add the vector store and object storage, and the
C‑level agent uses PostgreSQL and Kafka only.

## MemoryHub container

`MemoryHub` holds clients for all storage backends:

```python
from agents import MemoryHub

hub = MemoryHub(redis_client, pg_session, vector_dao, obj_client, kafka_producer)
```

When building agents you pass this hub but expose only the relevant
slice:

```python
from agents import (
    build_micro_agent,
    build_taskmaster,
    build_head,
    build_c_level,
)

micro = build_micro_agent("micro", some_tool, hub)
taskmaster = build_taskmaster("tm", orchestrate, hub)
head = build_head("head", plan_fn, hub)
executive = build_c_level("ceo", approve_fn, hub)
```

Each build function attaches just the required clients in the agent's
`memory` field.
