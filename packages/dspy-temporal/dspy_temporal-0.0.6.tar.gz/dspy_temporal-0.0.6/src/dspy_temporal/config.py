"""Configuration classes for DSPy-Temporal."""

from dataclasses import dataclass, field
from datetime import timedelta

from temporalio.common import RetryPolicy


def default_retry_policy() -> RetryPolicy:
    """Create the default retry policy for LLM activities."""
    return RetryPolicy(
        initial_interval=timedelta(seconds=1),
        backoff_coefficient=2.0,
        maximum_interval=timedelta(seconds=30),
        maximum_attempts=3,
        non_retryable_error_types=[
            # DSPy assertion errors
            "dspy.primitives.assertions.DSPyAssertionError",
            # Pydantic validation errors
            "pydantic.ValidationError",
            "pydantic_core._pydantic_core.ValidationError",
            # LiteLLM client errors (4xx)
            "litellm.BadRequestError",
            "litellm.AuthenticationError",
            "litellm.NotFoundError",
        ],
    )


@dataclass
class ActivityConfig:
    """Configuration for Temporal activities wrapping DSPy LLM calls.

    Attributes:
        start_to_close_timeout: Maximum time for a single activity attempt.
            Default is 60 seconds, suitable for most LLM calls.
        schedule_to_close_timeout: Maximum total time including retries.
        schedule_to_start_timeout: Maximum time waiting in queue.
        heartbeat_timeout: Maximum time between heartbeats for long-running activities.
        retry_policy: Retry configuration for failed activities.
    """

    start_to_close_timeout: timedelta = field(default_factory=lambda: timedelta(seconds=60))
    schedule_to_close_timeout: timedelta | None = None
    schedule_to_start_timeout: timedelta | None = None
    heartbeat_timeout: timedelta | None = None
    retry_policy: RetryPolicy | None = field(default_factory=default_retry_policy)

    def to_activity_options(self) -> dict:
        """Convert to kwargs for workflow.execute_activity."""
        options = {
            "start_to_close_timeout": self.start_to_close_timeout,
        }
        if self.schedule_to_close_timeout:
            options["schedule_to_close_timeout"] = self.schedule_to_close_timeout
        if self.schedule_to_start_timeout:
            options["schedule_to_start_timeout"] = self.schedule_to_start_timeout
        if self.heartbeat_timeout:
            options["heartbeat_timeout"] = self.heartbeat_timeout
        if self.retry_policy:
            options["retry_policy"] = self.retry_policy
        return options
