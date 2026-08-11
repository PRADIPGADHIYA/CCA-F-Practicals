"""
Exercise 4 — Step 1: programmatic gates.

A prompt rule ("classify before you draft") is advice the model can
ignore under pressure. A gate is a hard stop enforced by the Python
runtime: if the precondition for a step isn't met, we raise a named
exception with a clear message instead of letting the pipeline continue
with incomplete data.
"""


class PipelineGateError(Exception):
    """Raised when a pipeline step's precondition has not been satisfied."""


def gate_classification(ctx) -> None:
    """
    Raise PipelineGateError unless classification is fully complete.

    Names exactly which fields are still missing so the caller knows what
    to fix, rather than a generic "classification incomplete" message.
    """
    if ctx.classification_complete():
        return

    missing = [
        name
        for name, value in (
            ("product_area", ctx.product_area),
            ("severity", ctx.severity),
            ("intent", ctx.intent),
        )
        if value is None
    ]
    raise PipelineGateError(
        f"Gate 1 (classification) blocked — missing field(s): {', '.join(missing)}. "
        "Rerun the Classifier before proceeding to CRM enrichment."
    )


def gate_enrichment(ctx) -> None:
    """
    Raise PipelineGateError unless enrichment is fully complete.

    Names exactly which enrichment fields are None and instructs the
    caller to rerun the CRM Enricher.
    """
    if ctx.enrichment_complete():
        return

    missing = [
        name
        for name, value in (
            ("account_tier", ctx.account_tier),
            ("sla_tier", ctx.sla_tier),
        )
        if value is None
    ]
    raise PipelineGateError(
        f"Gate 2 (enrichment) blocked — missing field(s): {', '.join(missing)}. "
        "Rerun the CRM Enricher before proceeding to drafting."
    )


def gate_draft(ctx) -> None:
    """
    Raise PipelineGateError unless draft_response has been produced.

    Confirms draft_response is None and instructs the caller to rerun the
    Drafter.
    """
    if ctx.draft_complete():
        return

    raise PipelineGateError(
        "Gate 3 (draft) blocked — draft_response is None. "
        "Rerun the Drafter before proceeding to validation."
    )
