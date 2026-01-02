"""TemporalTool - Wrapper for tool functions to execute as Temporal activities."""

import asyncio
import logging
from typing import Any, Callable, TypeVar

from temporalio import activity, workflow

from dspy_temporal.config import ActivityConfig

logger = logging.getLogger(__name__)
T = TypeVar("T")


class TemporalTool:
    """Wraps a tool function for durable execution as a Temporal activity.

    When called inside a Temporal workflow, the tool executes as an activity.
    Outside a workflow, it executes directly.

    Example:
        ```python
        def calculator(expression: str) -> str:
            ...

        # Wrap the tool
        calculator_tool = TemporalTool(calculator, name="calculator")

        # In a workflow, this executes as an activity
        result = await calculator_tool.run(expression="2 + 2")
        ```

    Attributes:
        func: The wrapped tool function.
        name: Unique name for activity identification.
        activity_config: Configuration for activity execution.
    """

    def __init__(
        self,
        func: Callable[..., T],
        name: str | None = None,
        activity_config: ActivityConfig | None = None,
    ):
        """Initialize the TemporalTool wrapper.

        Args:
            func: The tool function to wrap.
            name: Unique name for activity identification. Defaults to function name.
            activity_config: Timeout and retry configuration.
        """
        self.func = func
        self.name = name or func.__name__
        self.activity_config = activity_config or ActivityConfig()

        # Validate name for Temporal compatibility
        if not self.name.replace("_", "").isalnum():
            raise ValueError(
                f"Tool name '{self.name}' contains invalid characters. "
                "Use only alphanumeric characters and underscores."
            )

        # Activity name
        self._activity_name = f"dspy__tool__{self.name}"

        # Create the activity
        self._activity = self._create_activity()

    def _create_activity(self) -> Callable:
        """Create the Temporal activity for this tool."""
        func = self.func

        @activity.defn(name=self._activity_name)
        async def tool_activity(params: dict[str, Any]) -> Any:
            """Execute the tool as a Temporal activity."""
            args = params.get("args", [])
            kwargs = params.get("kwargs", {})

            logger.debug(f"Executing tool '{func.__name__}' as activity with args={args}, kwargs={kwargs}")

            # Execute the tool function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            logger.debug(f"Tool '{func.__name__}' completed with result: {result}")
            return result

        return tool_activity

    @property
    def temporal_activities(self) -> list[Callable]:
        """Get the list of Temporal activities for this tool."""
        return [self._activity]

    async def run(self, *args: Any, **kwargs: Any) -> T:
        """Execute the tool, routing through Temporal activity if in workflow.

        Args:
            *args: Positional arguments for the tool.
            **kwargs: Keyword arguments for the tool.

        Returns:
            The result from the tool function.
        """
        # Check if we're in a workflow context
        try:
            in_workflow = workflow.in_workflow()
        except Exception:
            in_workflow = False

        if not in_workflow:
            # Direct execution outside workflow
            if asyncio.iscoroutinefunction(self.func):
                return await self.func(*args, **kwargs)
            else:
                return self.func(*args, **kwargs)

        # Execute as Temporal activity
        params = {"args": args, "kwargs": kwargs}
        return await workflow.execute_activity(
            self._activity,
            args=[params],
            **self.activity_config.to_activity_options(),
        )

    async def acall(self, *args: Any, **kwargs: Any) -> T:
        """Async execution interface for DSPy compatibility.

        DSPy's ReAct expects tools to have an acall() method for async execution.
        This delegates to run() which handles workflow vs non-workflow contexts.
        """
        return await self.run(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the tool synchronously or return coroutine for workflow context.

        When called outside a workflow, executes the function directly and returns
        the result. When called inside a workflow, returns a coroutine to be awaited.

        Note: DSPy agents use `acall()`, so this is primarily for manual invocations.

        Raises:
            RuntimeError: If tool is async and called synchronously outside workflow.
        """
        # Check if we're in a workflow context
        try:
            in_workflow = workflow.in_workflow()
        except Exception:
            in_workflow = False

        if in_workflow:
            # In workflow: return coroutine to be awaited
            return self.run(*args, **kwargs)

        # Outside workflow: execute directly
        if asyncio.iscoroutinefunction(self.func):
            raise RuntimeError(
                f"Tool '{self.name}' is async. Use 'await tool.run(...)' or 'await tool.acall(...)' instead."
            )
        return self.func(*args, **kwargs)


def temporal_tool(
    func: Callable[..., T] | None = None,
    *,
    name: str | None = None,
    activity_config: ActivityConfig | None = None,
) -> TemporalTool | Callable[[Callable[..., T]], TemporalTool]:
    """Decorator to wrap a tool function for Temporal durable execution.

    Can be used with or without arguments:

        @temporal_tool
        def my_tool(x: str) -> str:
            return x.upper()

        @temporal_tool(name="custom_name")
        def another_tool(x: int) -> int:
            return x * 2

    Args:
        func: The function to wrap (when used without parentheses).
        name: Optional custom name for the activity.
        activity_config: Optional activity configuration.

    Returns:
        A TemporalTool wrapper.
    """
    if func is not None:
        # Called without parentheses: @temporal_tool
        return TemporalTool(func, name=name, activity_config=activity_config)

    # Called with parentheses: @temporal_tool(name="...")
    def decorator(f: Callable[..., T]) -> TemporalTool:
        return TemporalTool(f, name=name, activity_config=activity_config)

    return decorator
