from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions
from temporalio.workflow import SandboxImportNotificationPolicy


def get_passthrough_modules() -> list[str]:
    """Get the list of modules that should be passthrough by the sandbox.

    These modules must be passthrough because they are part of DSPy's
    import dependency chain, even though they are not used in workflow code.

    ⚠️ IMPORTANT LIMITATION:
    While these HTTP libraries are in passthrough, they must NOT be used in
    workflow code. Due to Temporal's sandbox architecture, we cannot prevent
    users from importing these modules (since DSPy already imports them), but
    using them would cause non-deterministic behavior.

    The library enforces safety by:
    1. All LLM calls execute in activities (outside sandbox)
    2. Dynamic import warnings enabled to detect unusual imports
    3. Documentation clearly warns against HTTP usage in workflows

    Why passthrough is necessary:
    - DSPy eagerly imports: dspy → dspy.utils → requests → urllib3
    - Cannot block these imports without blocking DSPy itself
    - Tracking https://github.com/stanfordnlp/dspy/issues/8597 for upstream fix
    """
    return [
        "dspy",
        "litellm",
        "openai",
        "httpx",
        "urllib3",
    ]


def get_default_sandbox_restrictions() -> SandboxRestrictions:
    """Get sandbox restrictions with import monitoring.

    Uses WARN_ON_DYNAMIC_IMPORT policy to detect unusual import patterns
    that might indicate accidental HTTP usage in workflow code.
    """
    return SandboxRestrictions.default.with_passthrough_modules(
        *get_passthrough_modules()
    ).with_import_notification_policy(
        # Warn on dynamic imports to help catch accidental HTTP usage
        SandboxImportNotificationPolicy.WARN_ON_DYNAMIC_IMPORT
    )


def get_default_sandbox_runner(restrictions: SandboxRestrictions | None = None) -> SandboxedWorkflowRunner:
    if restrictions is None:
        restrictions = get_default_sandbox_restrictions()
    return SandboxedWorkflowRunner(restrictions=restrictions)
