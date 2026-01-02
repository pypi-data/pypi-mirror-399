"""Context tracking for DSPy-Temporal execution."""

import contextvars
from typing import Optional

# Tracks the name of the currently executing predictor within a TemporalModule.
# This is used to route LM calls to the correct per-predictor activity.
current_predictor: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("current_predictor", default=None)
