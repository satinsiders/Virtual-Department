from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .agent import Agent
from .memory.hub import HubSlice, MemoryHub
from .tool import function_tool


@dataclass
class DepartmentAgent(Agent[Any]):
    """Agent instance with attached memory slice."""

    memory: HubSlice | None = None


def build_micro_agent(name: str, tool_fn: Callable[..., Any], hub: MemoryHub) -> DepartmentAgent:
    """Create a micro agent with Redis-backed memory."""
    return DepartmentAgent(name=name, tools=[function_tool(tool_fn)], memory=hub.micro_slice())


def build_taskmaster(name: str, tool_fn: Callable[..., Any], hub: MemoryHub) -> DepartmentAgent:
    """Create a taskmaster agent with Redis and PostgreSQL access."""
    return DepartmentAgent(name=name, tools=[function_tool(tool_fn)], memory=hub.taskmaster_slice())


def build_head(name: str, tool_fn: Callable[..., Any], hub: MemoryHub) -> DepartmentAgent:
    """Create a head agent with access to object storage and the vector store."""
    return DepartmentAgent(name=name, tools=[function_tool(tool_fn)], memory=hub.head_slice())


def build_c_level(name: str, tool_fn: Callable[..., Any], hub: MemoryHub) -> DepartmentAgent:
    """Create a C-level agent with PostgreSQL and Kafka access."""
    return DepartmentAgent(name=name, tools=[function_tool(tool_fn)], memory=hub.c_level_slice())
