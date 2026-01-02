"""TemporalModule - Wrapper for DSPy modules to enable durable execution."""

import logging
from typing import Any, Callable, Generic, TypeVar

import dspy
from temporalio import activity, workflow

from dspy_temporal.config import ActivityConfig
from dspy_temporal.context import current_predictor
from dspy_temporal.lm import TemporalLM
from dspy_temporal.serialization import LMCallParams, LMCallResult
from dspy_temporal.tool import TemporalTool

logger = logging.getLogger(__name__)
OutputT = TypeVar("OutputT", bound=dspy.Prediction)


class TemporalModule(Generic[OutputT]):
    """Wraps a DSPy module for durable execution in Temporal workflows.

    This wrapper intercepts LLM calls made by the DSPy module and executes
    them as Temporal activities, providing:
    - Automatic checkpointing after each LLM call
    - Automatic retry on transient failures
    - Configurable timeouts
    - Workflow resumption from last successful step

    For agent modules (ReAct, Avatar, CodeAct, etc.), this also automatically
    wraps tools as TemporalTool instances, enabling tool calls to execute as
    Temporal activities with the same durability guarantees.

    Example:
        ```python
        # Wrap a DSPy agent with tools
        agent = dspy.ReAct("question -> answer", tools=[search, calculator])
        temporal_agent = TemporalModule(agent, name="my_agent")

        # Use in a workflow
        @workflow.defn
        class MyWorkflow:
            @workflow.run
            async def run(self, question: str) -> str:
                result = await temporal_agent.run(question=question)
                return result.answer
        ```

    Attributes:
        module: The wrapped DSPy module.
        name: Unique name for this module (used in activity names).
        activity_config: Configuration for activity execution.
        lm: Optional LM override (defaults to dspy.settings.lm).
    """

    def __init__(
        self,
        module: dspy.Module,
        name: str | None = None,
        activity_config: ActivityConfig | None = None,
        lm: dspy.LM | None = None,
    ):
        """Initialize the TemporalModule wrapper.

        Args:
            module: The DSPy module to wrap.
            name: Unique name for activity identification. Defaults to class name.
            activity_config: Timeout and retry configuration.
            lm: Optional LM to use (defaults to dspy.settings.lm at runtime).
        """
        self.module = module
        self.name = name or module.__class__.__name__
        self.activity_config = activity_config or ActivityConfig()
        self._lm = lm
        self._auto_wrapped_tools: list[TemporalTool] = []

        # Validate name for Temporal compatibility
        if not self.name.replace("_", "").isalnum():
            raise ValueError(
                f"Module name '{self.name}' contains invalid characters. "
                "Use only alphanumeric characters and underscores."
            )

        # Activity name prefix for uniqueness
        self._activity_prefix = f"dspy__{self.name}"

        # Discover predictors (direct child modules) for per-predictor activity naming
        self._predictors = self._discover_predictors()

        # Create per-predictor LM activities for better observability
        self._lm_activities = self._create_lm_activities()

        # Auto-wrap tools for agent modules (ReAct, Avatar, CodeAct, etc.)
        if hasattr(module, "tools") and module.tools:
            self._auto_wrap_tools()

    def _get_lm(self) -> dspy.LM:
        """Get the LM to use, falling back to global settings."""
        if self._lm is not None:
            return self._lm
        if dspy.settings.lm is None:
            raise ValueError("No LM configured. Either pass 'lm' to TemporalModule or configure dspy.settings.lm")
        return dspy.settings.lm

    def _discover_predictors(self) -> dict[str, dspy.Module]:
        """Discover direct child modules (predictors) in the wrapped module.

        This enables per-predictor activity naming for better observability
        in the Temporal dashboard.

        Returns:
            Dict mapping predictor names to their module instances.
        """
        predictors: dict[str, dspy.Module] = {}
        for name, value in self.module.__dict__.items():
            if isinstance(value, dspy.Module):
                # Validate predictor name for Temporal compatibility
                if name.replace("_", "").isalnum():
                    predictors[name] = value
                    logger.debug(f"Discovered predictor '{name}' ({type(value).__name__}) in module '{self.name}'")
                else:
                    logger.warning(
                        f"Skipping predictor '{name}' - name contains invalid characters for Temporal activity naming"
                    )
        return predictors

    def _create_lm_activity_impl(self, activity_name: str) -> Callable:
        """Create a single LM activity with the given name.

        Args:
            activity_name: The full activity name for Temporal.

        Returns:
            The activity function.
        """
        temporal_module = self

        @activity.defn(name=activity_name)
        async def lm_call_activity(params_dict: dict[str, Any]) -> dict[str, Any]:
            """Execute an LLM call as a Temporal activity."""
            params = LMCallParams.from_dict(params_dict)
            lm = temporal_module._get_lm()

            # Execute the LLM call
            if hasattr(lm, "acall"):
                outputs = await lm.acall(messages=params.messages, **params.kwargs)
            else:
                outputs = lm(messages=params.messages, **params.kwargs)

            # Get usage from history if available
            usage = None
            if lm.history:
                last_entry = lm.history[-1]
                usage = last_entry.get("usage")

            result = LMCallResult(outputs=outputs, usage=usage)
            return result.to_dict()

        return lm_call_activity

    def _create_lm_activities(self) -> dict[str | None, Callable]:
        """Create Temporal activities for LLM calls, one per predictor.

        Each predictor gets its own activity for better observability:
        - dspy__<module>__<predictor>__lm_call for each predictor
        - dspy__<module>__lm_call as fallback for unknown predictors

        Returns:
            Dict mapping predictor names (or None for fallback) to activities.
        """
        activities: dict[str | None, Callable] = {}

        # Create activity for each discovered predictor
        for predictor_name in self._predictors:
            activity_name = f"{self._activity_prefix}__{predictor_name}__lm_call"
            activities[predictor_name] = self._create_lm_activity_impl(activity_name)
            logger.debug(f"Created activity '{activity_name}' for predictor '{predictor_name}'")

        # Fallback activity for unknown predictors or direct LM calls
        fallback_name = f"{self._activity_prefix}__lm_call"
        activities[None] = self._create_lm_activity_impl(fallback_name)
        logger.debug(f"Created fallback activity '{fallback_name}'")

        return activities

    @property
    def temporal_activities(self) -> list[Callable]:
        """Get the list of Temporal activities for this module.

        These activities should be registered with the Temporal worker.
        Includes per-predictor LM activities and auto-wrapped tool activities.
        """
        # All LM activities (per-predictor + fallback)
        activities = list(self._lm_activities.values())

        # Tool activities
        for tool in self._auto_wrapped_tools:
            activities.extend(tool.temporal_activities)

        return activities

    async def run(self, **kwargs: Any) -> OutputT:
        """Execute the DSPy module with durable execution.

        When called inside a Temporal workflow, LLM calls are executed as
        activities and automatically checkpointed. Outside a workflow,
        the module executes normally.

        Args:
            **kwargs: Input arguments passed to the DSPy module's forward method.

        Returns:
            The Prediction result from the DSPy module.
        """
        # Check if we're in a workflow context
        try:
            in_workflow = workflow.in_workflow()
        except Exception:
            in_workflow = False

        if not in_workflow:
            # Direct execution outside workflow
            logger.debug(f"Executing module '{self.name}' directly (not in workflow)")
            return self.module(**kwargs)

        # Create a TemporalLM that routes calls through activities
        logger.debug(f"Executing module '{self.name}' in workflow context with Temporal activities")
        original_lm = self._get_lm()
        temporal_lm = TemporalLM(
            original_lm=original_lm,
            activities=self._lm_activities,
            activity_config=self.activity_config,
        )

        # Wrap predictor acall methods to set context for activity routing
        original_acalls = self._wrap_predictor_acalls()

        try:
            # Execute module with the temporal LM using async path
            with dspy.context(lm=temporal_lm):
                # IMPORTANT: We must use the async path (acall) for Temporal compatibility.
                # The module must implement aforward() with async sub-module calls.
                # If aforward() is not implemented, acall() will fail.
                return await self.module.acall(**kwargs)
        finally:
            # Restore original acall methods
            self._restore_predictor_acalls(original_acalls)

    def _wrap_predictor_acalls(self) -> dict[str, Callable]:
        """Wrap each predictor's acall method to set context for activity routing.

        Returns:
            Dict mapping predictor names to their original acall methods.
        """
        original_acalls: dict[str, Callable] = {}

        for name, predictor in self._predictors.items():
            if hasattr(predictor, "acall"):
                original_acalls[name] = predictor.acall
                predictor.acall = self._create_context_wrapped_acall(name, predictor.acall)

        return original_acalls

    def _create_context_wrapped_acall(self, predictor_name: str, original_acall: Callable) -> Callable:
        """Create a wrapped acall that sets the predictor context.

        Args:
            predictor_name: Name of the predictor for context tracking.
            original_acall: The original acall method to wrap.

        Returns:
            Wrapped async function that sets context before calling original.
        """

        async def wrapped_acall(*args: Any, **kwargs: Any) -> Any:
            token = current_predictor.set(predictor_name)
            try:
                return await original_acall(*args, **kwargs)
            finally:
                current_predictor.reset(token)

        return wrapped_acall

    def _restore_predictor_acalls(self, original_acalls: dict[str, Callable]) -> None:
        """Restore original acall methods on predictors.

        Args:
            original_acalls: Dict mapping predictor names to original acall methods.
        """
        for name, original_acall in original_acalls.items():
            if name in self._predictors:
                self._predictors[name].acall = original_acall

    def __call__(self, **kwargs: Any) -> OutputT:
        """Synchronous execution of the module.

        Note: Inside a Temporal workflow, use `await module.run(...)` instead.
        """
        return self.module(**kwargs)

    def _auto_wrap_tools(self) -> None:
        """Wrap DSPy agent tools with TemporalTool for durable execution.

        Works with any DSPy module that has a 'tools' attribute, including:
        - ReAct (stores tools as dict)
        - Avatar (stores tools as list)
        - CodeAct (inherits from ReAct, uses dict)
        """
        tools_attr = getattr(self.module, "tools", None)
        if not tools_attr:
            return

        # Handle both dict (ReAct, CodeAct) and list (Avatar) tool storage
        tools_to_wrap = tools_attr.values() if isinstance(tools_attr, dict) else tools_attr

        wrapped_tools: dict[str, TemporalTool] | list[TemporalTool] = {} if isinstance(tools_attr, dict) else []
        for idx, tool in enumerate(tools_to_wrap):
            if isinstance(tool, TemporalTool):
                wrapped_tool = tool
            else:
                # For DSPy Tool objects, wrap the underlying func
                func = getattr(tool, "func", tool)
                # Prefer the tool's name over function name (handles lambdas and other edge cases)
                tool_name = getattr(tool, "name", None) or getattr(func, "__name__", None) or f"tool_{idx}"
                # Sanitize name for Temporal (lambda functions have "<lambda>" as name)
                if tool_name == "<lambda>":
                    tool_name = getattr(tool, "name", f"lambda_tool_{idx}")

                logger.debug(f"Auto-wrapping tool '{tool_name}' as TemporalTool")
                wrapped_tool = TemporalTool(
                    func,
                    name=tool_name,
                    activity_config=self.activity_config,
                )

            # Store in the same structure (dict or list)
            if isinstance(wrapped_tools, dict):
                key = tool.name if hasattr(tool, "name") else tool_name
                wrapped_tools[key] = wrapped_tool
            else:
                wrapped_tools.append(wrapped_tool)

            self._auto_wrapped_tools.append(wrapped_tool)

        # Replace tools on the module so ReAct uses Temporal-aware wrappers
        if wrapped_tools:
            logger.debug(f"Replaced {len(wrapped_tools)} tools on module '{self.name}' with TemporalTool wrappers")
            self.module.tools = wrapped_tools
