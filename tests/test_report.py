"""Build steps 4-5: text and JSON reports (spec §7).

Un-skip and complete these when implementing ``tattletale.report``. Step 4
proves the text output is legible to someone who has never seen the repo;
step 5 gives machine consumers a stable shape.
"""

import pytest

STEP_4 = pytest.mark.skip(reason="Build step 4 not implemented: text report (spec §7)")
STEP_5 = pytest.mark.skip(reason="Build step 5 not implemented: JSON report (spec §7)")


@STEP_4
def test_header_shows_total_claims_and_failures():
    ...


@STEP_4
def test_header_shows_source_name_and_normalized_hash():
    ...


@STEP_4
def test_agent_blocks_show_per_agent_counts():
    ...


@STEP_4
def test_failed_claims_show_quote_reason_and_origin():
    """``originated here`` vs ``inherited from: <agent> (<claim_id>)``."""
    ...


@STEP_4
def test_agents_with_zero_failures_still_appear():
    """A summarizer that submitted zero claims is itself a finding (spec §7)."""
    ...


@STEP_5
def test_json_report_parses_and_carries_source_hashes():
    ...


@STEP_5
def test_json_report_includes_passing_claims():
    """JSON carries the same content as text plus every passing claim
    (spec §7)."""
    ...
