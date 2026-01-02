"""DSPy-Temporal: Durable execution for DSPy programs using Temporal."""

from dspy_temporal.config import ActivityConfig
from dspy_temporal.lm import TemporalLM
from dspy_temporal.module import TemporalModule
from dspy_temporal.plugin import DSPyPlugin, collect_activities
from dspy_temporal.tool import TemporalTool, temporal_tool
from dspy_temporal.workflow import DSPyWorkflow

__all__ = [
    "ActivityConfig",
    "DSPyPlugin",
    "DSPyWorkflow",
    "TemporalLM",
    "TemporalModule",
    "TemporalTool",
    "collect_activities",
    "temporal_tool",
]

__version__ = "0.0.1"
