"""Base decision engine contract for V2 migration."""
from __future__ import annotations

from typing import Any, Protocol


class BaseDecisionEngine(Protocol):
    """Abstract protocol for decision engines."""

    engine_name: str

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Run the engine with normalized analysis payload."""
        raise NotImplementedError
