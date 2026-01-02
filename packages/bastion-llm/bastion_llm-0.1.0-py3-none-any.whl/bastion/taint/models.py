"""Data models for taint analysis."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaintSource:
    """A source of tainted (user-controlled) data."""

    name: str
    node: Any
    line: int
    source_type: str  # "request", "parameter", "database", "file", "environment"


@dataclass
class TaintSink:
    """A sink where tainted data could be dangerous."""

    name: str
    node: Any
    line: int
    sink_type: str  # "llm_call", "prompt_construction", "system_message"


@dataclass
class TaintFlow:
    """A flow of tainted data from source to sink."""

    source: TaintSource
    sink: TaintSink
    path: list[str] = field(default_factory=list)  # Variable names in the flow
