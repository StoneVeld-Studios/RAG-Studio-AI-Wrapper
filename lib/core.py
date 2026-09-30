"""Engine-neutral Core boundary for RAG Trigger Studio.

The application talks to a Core, not directly to a particular engine.
Providers implement the transport details behind that boundary.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CoreRequest:
    context: str
    instructions: str


@dataclass(frozen=True)
class CoreResponse:
    text: str
    provider: str
    model: str
    context_limit: int


class CoreProvider(Protocol):
    """Minimal contract used by the application and deterministic tests."""

    @property
    def provider_name(self) -> str: ...

    def context_limit(self) -> int: ...

    def generate(self, request: CoreRequest) -> CoreResponse: ...
