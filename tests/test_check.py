"""Build step 2: ``Monitor.check`` with reason codes, no lineage (spec §4, §5).

Un-skip and complete these when implementing ``tattletale.monitor``. The step
proves fabricated quotes are rejected — every verdict binary, every failure
carrying exactly one reason code.
"""

import pytest

STEP_2 = pytest.mark.skip(reason="Build step 2 not implemented: Monitor.check (spec §4, §5)")


@STEP_2
def test_exact_quote_passes():
    ...


@STEP_2
def test_fabricated_quote_fails_not_in_source():
    ...


@STEP_2
def test_quote_present_after_normalization_passes():
    """A curly-quoted claim against a straight-quoted source still passes —
    both sides normalize identically (spec §5.1)."""
    ...


@STEP_2
def test_unloaded_document_fails_unknown_source():
    ...


@STEP_2
def test_whitespace_only_quote_fails_empty_quote():
    ...


@STEP_2
def test_passing_claim_has_no_reason_code():
    """A claim that passes gets no code; every failure gets exactly one
    (spec §5.2)."""
    ...


@STEP_2
def test_check_returns_results_and_records_them():
    """check() returns the result list for the batch and accumulates results
    for report() (spec §4)."""
    ...
