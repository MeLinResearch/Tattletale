"""Build step 8: the adversarial suite (spec §9). The step that matters.

Tests that feed the checker valid claims prove nothing. Each attack below has
an expected verdict AND an expected named agent. Un-skip these last — they
exercise the whole pipeline end to end.
"""

import pytest

STEP_8 = pytest.mark.skip(reason="Build step 8 not implemented: adversarial suite (spec §9)")


@STEP_8
def test_smart_quotes_against_straight_quote_source():
    """Curly quotes in the claim, straight quotes in the source: PASSED —
    normalization makes them identical, and a false failure here would be a
    wrong verdict."""
    ...


@STEP_8
def test_quote_spanning_a_hyphenated_line_break():
    """The source hyphenates a word across a line break; the claim quotes it
    joined: PASSED after soft-hyphen repair."""
    ...


@STEP_8
def test_claim_citing_a_document_that_was_never_loaded():
    """UNKNOWN_SOURCE, attributed to the submitting agent."""
    ...


@STEP_8
def test_lineage_cycle():
    """Walk capped at the number of recorded claims; chain reported broken."""
    ...


@STEP_8
def test_parent_id_that_was_never_submitted():
    """BROKEN_LINEAGE naming the last known agent."""
    ...


@STEP_8
def test_agent_that_subtly_rewords_a_valid_upstream_quote():
    """Upstream claim PASSED; the reworded child FAILED with NOT_IN_SOURCE
    and the child agent named as origin — not the clean upstream agent."""
    ...
