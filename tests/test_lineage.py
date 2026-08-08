"""Build step 3: the lineage walk and its three edge cases (spec §6).

Un-skip and complete these when implementing ``tattletale.lineage``. The step
proves the origin is named correctly, including reword-in-the-middle.
"""

import pytest

STEP_3 = pytest.mark.skip(reason="Build step 3 not implemented: lineage walk (spec §6)")


@STEP_3
def test_walks_chain_to_root_and_names_origin_agent():
    """summarizer -> editor -> researcher: a failure at the end of the chain
    is attributed to researcher, the agent with no parent."""
    ...


@STEP_3
def test_new_claim_with_no_parent_originates_at_submitter():
    ...


@STEP_3
def test_missing_parent_reports_broken_lineage_with_last_known_agent():
    """Edge case 1: parent id never checked. BROKEN_LINEAGE, and the last
    known agent is named — never silently attributed to the submitter."""
    ...


@STEP_3
def test_cycle_is_capped_and_reported_as_broken():
    """Edge case 2: the walk is capped at the number of recorded claims and
    reports the chain as broken on overrun."""
    ...


@STEP_3
def test_reworded_quote_originates_at_the_child_not_the_parent():
    """Edge case 3: parent passed but child failed — the child altered the
    quote, so the child is the origin. This is the case that earns the name."""
    ...
