from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryHub:
    """Container for durable memory clients."""

    redis: Any
    """Redis client for short-lived caches."""

    pg: Any
    """PostgreSQL session or connection."""

    vec: Any
    """Vector store data access object."""

    obj: Any
    """Object storage client."""

    kafka: Any
    """Kafka producer for audit events."""

    def micro_slice(self) -> HubSlice:
        """Return the subset of the hub used by micro agents."""
        return HubSlice(redis=self.redis)

    def taskmaster_slice(self) -> HubSlice:
        """Return the subset used by taskmaster agents."""
        return HubSlice(redis=self.redis, pg=self.pg)

    def head_slice(self) -> HubSlice:
        """Return the subset used by head agents."""
        return HubSlice(redis=self.redis, pg=self.pg, vec=self.vec, obj=self.obj)

    def c_level_slice(self) -> HubSlice:
        """Return the subset used by C-level agents."""
        return HubSlice(pg=self.pg, kafka=self.kafka)


@dataclass
class HubSlice:
    """A partial view of a :class:`MemoryHub`."""

    redis: Any | None = None
    pg: Any | None = None
    vec: Any | None = None
    obj: Any | None = None
    kafka: Any | None = None
