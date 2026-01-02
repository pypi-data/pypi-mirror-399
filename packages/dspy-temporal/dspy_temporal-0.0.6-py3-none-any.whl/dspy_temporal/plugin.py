"""DSPyPlugin - Temporal plugin for automatic activity registration."""

from typing import Any, Callable, Union

from temporalio.plugin import SimplePlugin

from dspy_temporal.module import TemporalModule
from dspy_temporal.tool import TemporalTool


class DSPyPlugin(SimplePlugin):
    """Temporal plugin that auto-registers DSPy module activities.

    Supports two usage patterns:

    **Pattern 1: Explicit Registration (Recommended)**
        Pass modules and tools directly to the plugin:

        ```python
        async with Worker(
            client,
            task_queue="my-queue",
            workflows=[MyWorkflow],
            plugins=[DSPyPlugin(temporal_agent, tool1, tool2)],
        ):
            # Activities from temporal_agent, tool1, and tool2 are auto-registered
            ...
        ```

    **Pattern 2: Auto-Discovery via Workflow Metadata**
        Use `__dspy_modules__` class attribute on workflows:

        ```python
        @workflow.defn
        class MyWorkflow:
            __dspy_modules__ = [temporal_agent]

            @workflow.run
            async def run(self, prompt: str) -> str:
                return await temporal_agent.aforward(prompt)

        async with Worker(
            client,
            task_queue="my-queue",
            workflows=[MyWorkflow],
            plugins=[DSPyPlugin()],  # Auto-discovers from __dspy_modules__
        ):
            ...
        ```

    Args:
        *items: TemporalModule or TemporalTool instances to register.
            If provided, uses explicit registration (Pattern 1).
            If empty, falls back to auto-discovery (Pattern 2).

    Raises:
        TypeError: If any item is not a TemporalModule or TemporalTool.
    """

    def __init__(self, *items: Union[TemporalModule[Any], TemporalTool]) -> None:
        """Initialize the plugin with optional modules/tools.

        Args:
            *items: TemporalModule or TemporalTool instances to register.

        Raises:
            TypeError: If any item is not a TemporalModule or TemporalTool.
        """
        # Validate all items
        for item in items:
            if not isinstance(item, (TemporalModule, TemporalTool)):
                raise TypeError(
                    f"DSPyPlugin only accepts TemporalModule or TemporalTool instances. "
                    f"Got {type(item).__name__}: {item}"
                )

        self._items = items

        # Initialize SimplePlugin base class
        super().__init__(name="DSPyPlugin")

    def configure_worker(self, config: dict[str, Any]) -> dict[str, Any]:
        """Configure the worker with DSPy activities.

        This is called by Temporal when setting up a worker.
        Supports two patterns:
        1. Explicit items (passed to __init__) - takes precedence
        2. Auto-discovery from workflow __dspy_modules__ attributes

        Args:
            config: Worker configuration dictionary.

        Returns:
            Updated configuration with DSPy activities added.
        """
        # Call parent configure_worker first (important for plugin chain)
        config = super().configure_worker(config)

        activities: list[Callable[..., Any]] = list(config.get("activities", []))

        # Pattern 1: Explicit items (if provided to __init__)
        if self._items:
            for item in self._items:
                activities.extend(item.temporal_activities)

        # Pattern 2: Auto-discovery from __dspy_modules__ (backward compatible)
        else:
            workflows = config.get("workflows", [])
            for workflow_cls in workflows:
                dspy_modules = getattr(workflow_cls, "__dspy_modules__", None)
                if dspy_modules is not None:
                    for module in dspy_modules:
                        if isinstance(module, TemporalModule):
                            activities.extend(module.temporal_activities)

        config["activities"] = activities
        return config


def collect_activities(
    *items: Union[TemporalModule[Any], TemporalTool],
) -> list[Callable[..., Any]]:
    """Collect all activities from TemporalModules and TemporalTools.

    Utility function for manual activity registration.

    Args:
        *items: TemporalModule or TemporalTool instances to collect activities from.

    Returns:
        List of activity functions.

    Example:
        ```python
        activities = collect_activities(module1, module2, calculator_tool)
        async with Worker(
            client,
            task_queue="my-queue",
            workflows=[MyWorkflow],
            activities=activities,
        ):
            ...
        ```
    """
    activities: list[Callable[..., Any]] = []
    for item in items:
        activities.extend(item.temporal_activities)
    return activities
