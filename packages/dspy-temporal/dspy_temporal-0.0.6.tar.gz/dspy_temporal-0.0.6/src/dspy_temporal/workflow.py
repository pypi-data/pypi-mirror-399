"""DSPyWorkflow - Base class for workflows using DSPy modules."""

from typing import Any, Callable, ClassVar

from dspy_temporal.module import TemporalModule


class DSPyWorkflow:
    """Base class for Temporal workflows that use DSPy modules.

    Subclass this to create workflows that automatically register
    DSPy module activities.

    Example:
        ```python
        @workflow.defn
        class MyWorkflow(DSPyWorkflow):
            __dspy_modules__ = [temporal_module]

            @workflow.run
            async def run(self, input: str) -> str:
                result = await temporal_module.run(input=input)
                return result.output
        ```

    Attributes:
        __dspy_modules__: List of TemporalModule instances to register.
    """

    __dspy_modules__: ClassVar[list[TemporalModule[Any]]] = []

    @classmethod
    def get_activities(cls) -> list[Callable[..., Any]]:
        """Get all activities from registered DSPy modules.

        Returns:
            List of activity functions to register with the worker.
        """
        activities: list[Callable[..., Any]] = []
        for module in cls.__dspy_modules__:
            activities.extend(module.temporal_activities)
        return activities
