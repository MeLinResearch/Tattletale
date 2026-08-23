"""Build step 8: the adversarial suite (spec §9). The step that matters.

Tests that feed the checker valid claims prove nothing. Each attack below has
an expected verdict AND an expected named agent. Un-skip these last — they
exercise the whole pipeline end to end.
"""

from tattletale import (
    BROKEN_LINEAGE,
    NOT_IN_SOURCE,
    UNKNOWN_SOURCE,
    Claim,
    Monitor,
)


def test_smart_quotes_against_straight_quote_source():
    """Curly quotes in the claim, straight quotes in the source: PASSED —
    normalization makes them identical, and a false failure here would be a
    wrong verdict."""
    monitor = Monitor({"contract.txt": 'The service is called "Ada\'s plan".'})

    result = monitor.check(
        "researcher", [Claim("c_001", "“Ada’s plan”", "contract.txt")]
    )[0]

    assert result.status == "PASSED"
    assert result.reason is None


def test_quote_spanning_a_hyphenated_line_break():
    """The source hyphenates a word across a line break; the claim quotes it
    joined: PASSED after soft-hyphen repair."""
    monitor = Monitor({"contract.txt": "The term renews auto-\nmatically."})

    result = monitor.check(
        "researcher", [Claim("c_001", "renews automatically", "contract.txt")]
    )[0]

    assert result.status == "PASSED"
    assert result.reason is None


def test_claim_citing_a_document_that_was_never_loaded():
    """UNKNOWN_SOURCE, attributed to the submitting agent."""
    monitor = Monitor({"contract.txt": "real clause"})

    result = monitor.check(
        "researcher", [Claim("c_001", "real clause", "missing.txt")]
    )[0]

    assert result.reason == UNKNOWN_SOURCE
    assert (result.origin_agent, result.origin_claim_id) == ("researcher", "c_001")


def test_lineage_cycle():
    """Walk capped at the number of recorded claims; chain reported broken."""
    monitor = Monitor({"contract.txt": "real clause"})
    results = monitor.check(
        "researcher",
        [
            Claim("c_001", "real clause", "contract.txt", derived_from="c_002"),
            Claim("c_002", "invented clause", "contract.txt", derived_from="c_001"),
        ],
    )

    assert all(result.reason == BROKEN_LINEAGE for result in results)


def test_parent_id_that_was_never_submitted():
    """BROKEN_LINEAGE naming the last known agent."""
    monitor = Monitor({"contract.txt": "real clause"})

    result = monitor.check(
        "editor",
        [Claim("c_002", "real clause", "contract.txt", derived_from="missing")],
    )[0]

    assert result.reason == BROKEN_LINEAGE
    assert (result.origin_agent, result.origin_claim_id) == ("editor", "c_002")


def test_agent_that_subtly_rewords_a_valid_upstream_quote():
    """Upstream claim PASSED; the reworded child FAILED with NOT_IN_SOURCE
    and the child agent named as origin — not the clean upstream agent."""
    monitor = Monitor({"contract.txt": "The term renews every 12 months."})
    monitor.check(
        "researcher", [Claim("c_001", "renews every 12 months", "contract.txt")]
    )

    result = monitor.check(
        "editor",
        [
            Claim(
                "c_002",
                "renews automatically every 12 months",
                "contract.txt",
                derived_from="c_001",
            )
        ],
    )[0]

    assert result.reason == NOT_IN_SOURCE
    assert (result.origin_agent, result.origin_claim_id) == ("editor", "c_002")


def test_repeated_runs_produce_identical_reports():
    def run() -> tuple[str, str]:
        monitor = Monitor({"contract.txt": "real clause"})
        monitor.check(
            "researcher", [Claim("c_001", "invented clause", "contract.txt")]
        )
        return monitor.report(), monitor.report(format="json")

    assert run() == run()
