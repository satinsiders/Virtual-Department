from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any


class VectorStoreDAO:
    """Placeholder vector store access object."""

    def add_embedding(self, data: Any) -> None:
        pass


class ObjectStorageClient:
    """Placeholder object storage client."""

    def upload_file(self, path: str, data: bytes) -> None:
        pass


class KafkaProducer:
    """Placeholder Kafka producer."""

    def produce(self, event: dict[str, Any]) -> None:
        pass


@dataclass
class MemoryHub:
    """Container holding all memory related clients."""

    redis: Any
    pg: sqlite3.Connection
    vec: VectorStoreDAO
    obj: ObjectStorageClient
    kafka: KafkaProducer
