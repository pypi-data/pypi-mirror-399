"""TemporalLM - LM wrapper that executes calls as Temporal activities."""

from typing import Any, Callable

import dspy
from temporalio import workflow

from dspy_temporal.config import ActivityConfig
from dspy_temporal.context import current_predictor
from dspy_temporal.serialization import LMCallParams, LMCallResult


class TemporalLM(dspy.LM):
    """LM wrapper that executes LLM calls as Temporal activities.

    When used inside a Temporal workflow, this LM routes all calls through
    a Temporal activity, providing durability and automatic retries.
    Outside of a workflow, it delegates to the original LM directly.

    The LM supports per-predictor activity routing for better observability.
    Each predictor in a module gets its own activity name, making it easy
    to identify which predictor failed in the Temporal UI.

    Attributes:
        original_lm: The underlying DSPy LM to use for actual calls.
        activities: Dict mapping predictor names to their activities.
                   None key is the fallback activity.
        activity_config: Configuration for activity execution.
    """

    def __init__(
        self,
        original_lm: dspy.LM,
        activities: dict[str | None, Callable],
        activity_config: ActivityConfig,
    ):
        """Initialize the TemporalLM wrapper.

        Args:
            original_lm: The DSPy LM to wrap.
            activities: Dict mapping predictor names (or None for fallback)
                       to their activity functions.
            activity_config: Timeout and retry configuration.
        """
        # Initialize parent with same model string
        super().__init__(model=original_lm.model)
        self.original_lm = original_lm
        self.activities = activities
        self.activity_config = activity_config
        self.history: list[dict[str, Any]] = []

    def __call__(
        self,
        prompt: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        """Execute an LLM call, routing through Temporal activity if in workflow.

        Args:
            prompt: Optional prompt string (converted to messages internally).
            messages: List of message dicts for the LLM.
            **kwargs: Additional arguments passed to the LLM.

        Returns:
            List of output strings from the LLM.
        """
        # Convert prompt to messages if needed
        if messages is None and prompt is not None:
            messages = [{"role": "user", "content": prompt}]
        elif messages is None:
            messages = []

        # Check if we're in a workflow context
        try:
            in_workflow = workflow.in_workflow()
        except Exception:
            in_workflow = False

        if not in_workflow:
            # Direct execution outside workflow
            return self.original_lm(messages=messages, **kwargs)

        # Sync LM calls inside a workflow are not supported.
        # DSPy modules must use the async path for Temporal compatibility.
        raise RuntimeError(
            "TemporalLM was called synchronously inside a Temporal workflow. "
            "DSPy-Temporal requires async modules. Your module must:\n"
            "  1. Implement 'async def aforward(self, ...)' instead of 'def forward(self, ...)'\n"
            "  2. Use 'await self.predictor.acall(...)' instead of 'self.predictor(...)'\n"
            "See the examples for async module patterns."
        )

    async def acall(
        self,
        prompt: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        """Async execute an LLM call as a Temporal activity.

        Args:
            prompt: Optional prompt string.
            messages: List of message dicts for the LLM.
            **kwargs: Additional arguments passed to the LLM.

        Returns:
            List of output strings from the LLM.
        """
        # Convert prompt to messages if needed
        if messages is None and prompt is not None:
            messages = [{"role": "user", "content": prompt}]
        elif messages is None:
            messages = []

        # Check if we're in a workflow context
        try:
            in_workflow = workflow.in_workflow()
        except Exception:
            in_workflow = False

        if not in_workflow:
            # Direct execution outside workflow
            if hasattr(self.original_lm, "acall"):
                return await self.original_lm.acall(messages=messages, **kwargs)
            return self.original_lm(messages=messages, **kwargs)

        # Prepare activity parameters
        params = LMCallParams(
            model=self.original_lm.model,
            messages=messages,
            kwargs=kwargs,
        )

        # Select activity based on current predictor context
        predictor_name = current_predictor.get()
        activity = self.activities.get(predictor_name) or self.activities[None]

        # Execute as Temporal activity
        result_dict = await workflow.execute_activity(
            activity,
            args=[params.to_dict()],
            **self.activity_config.to_activity_options(),
        )
        result = LMCallResult.from_dict(result_dict)

        # Update history for DSPy compatibility
        self.history.append(
            {
                "messages": messages,
                "outputs": result.outputs,
                "usage": result.usage,
                "model": self.original_lm.model,
            }
        )

        return result.outputs
