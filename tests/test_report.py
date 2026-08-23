"""Build steps 4-5: text and JSON reports (spec §7).

Un-skip and complete these when implementing ``tattletale.report``. Step 4
proves the text output is legible to someone who has never seen the repo;
step 5 gives machine consumers a stable shape.
"""

import pytest

from tattletale import Claim, Monitor

STEP_5 = pytest.mark.skip(reason="Build step 5 not implemented: JSON report (spec §7)")


def test_header_shows_total_claims_and_failures():
    monitor = Monitor({"contract.txt": "real clause"})
    monitor.check(
        "researcher",
        [
            Claim("c_001", "real clause", "contract.txt"),
            Claim("c_002", "invented clause", "contract.txt"),
        ],
    )

    assert "TATTLETALE    2 claims     1 failed" in monitor.report()


def test_header_shows_source_name_and_normalized_hash():
    monitor = Monitor({"contract.txt": "  real\nclause  "})

    report = monitor.report()

    assert "source: contract.txt" in report
    assert f"sha256:{monitor._source_hashes['contract.txt']} (normalized)" in report


def test_agent_blocks_show_per_agent_counts():
    monitor = Monitor({"contract.txt": "real clause"})
    monitor.check("researcher", [Claim("c_001", "real clause", "contract.txt")])
    monitor.check("editor", [Claim("c_002", "invented clause", "contract.txt")])

    report = monitor.report()

    assert "researcher          1 claims     0 FAILED" in report
    assert "editor          1 claims     1 FAILED" in report


def test_failed_claims_show_quote_reason_and_origin():
    """``originated here`` vs ``inherited from: <agent> (<claim_id>)``."""
    monitor = Monitor({"contract.txt": "real clause"})
    monitor.check("researcher", [Claim("c_001", "invented\nclause", "contract.txt")])
    monitor.check(
        "editor",
        [Claim("c_002", "invented clause", "contract.txt", derived_from="c_001")],
    )

    report = monitor.report()

    assert 'c_001     "invented clause"' in report
    assert "NOT_IN_SOURCE" in report
    assert "originated here" in report
    assert "inherited from: researcher (c_001)" in report


def test_agents_with_zero_failures_still_appear():
    """A summarizer that submitted zero claims is itself a finding (spec §7)."""
    monitor = Monitor({"contract.txt": "real clause"})
    monitor.check("researcher", [Claim("c_001", "real clause", "contract.txt")])
    monitor.check("summarizer", [])

    report = monitor.report()

    assert "researcher          1 claims     0 FAILED" in report
    assert "summarizer          0 claims     0 FAILED" in report


def test_broken_lineage_is_not_reported_as_originated_here():
    monitor = Monitor({"contract.txt": "real clause"})
    monitor.check(
        "summarizer",
        [Claim("c_001", "real clause", "contract.txt", derived_from="missing")],
    )

    report = monitor.report()

    assert "lineage broken after: summarizer (c_001)" in report
    assert "originated here" not in report


@STEP_5
def test_json_report_parses_and_carries_source_hashes():
    ...


@STEP_5
def test_json_report_includes_passing_claims():
    """JSON carries the same content as text plus every passing claim
    (spec §7)."""
    ...
