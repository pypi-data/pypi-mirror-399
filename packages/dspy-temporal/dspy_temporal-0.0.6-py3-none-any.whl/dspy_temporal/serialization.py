"""Serialization utilities for LLM call parameters and results."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class LMCallParams:
    """Parameters for an LLM call activity.

    Attributes:
        model: Model identifier (e.g., "openai/gpt-5-mini").
        messages: List of message dicts for the LLM.
        kwargs: Additional keyword arguments for the LLM call.
    """

    model: str
    messages: list[dict[str, Any]]
    kwargs: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LMCallParams":
        """Create from dictionary."""
        return cls(
            model=data["model"],
            messages=data["messages"],
            kwargs=data["kwargs"],
        )


@dataclass
class LMCallResult:
    """Result from an LLM call activity.

    Attributes:
        outputs: List of output strings from the LLM.
        usage: Token usage information (input_tokens, output_tokens).
    """

    outputs: list[str]
    usage: dict[str, int] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LMCallResult":
        """Create from dictionary."""
        return cls(
            outputs=data["outputs"],
            usage=data.get("usage"),
        )
