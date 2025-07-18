from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AgentPayload(BaseModel):
    """Input payload sent to an agent."""

    agent_id: str
    inputs: dict[str, Any]


class StateCheckpoint(BaseModel):
    """Persisted agent state."""

    agent_id: str
    status: str
    retry_count: int = 0


class ArtifactManifest(BaseModel):
    """Metadata for stored artifacts."""

    artifact_id: str
    files: list[str]
