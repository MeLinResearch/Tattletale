"""Build step 3: the lineage walk and its three edge cases (spec §6).

Un-skip and complete these when implementing ``tattletale.lineage``. The step
proves the origin is named correctly, including reword-in-the-middle.
"""

from tattletale import BROKEN_LINEAGE, NOT_IN_SOURCE, Claim, Monitor


def test_walks_chain_to_root_and_names_origin_agent():
    """summarizer -> editor -> researcher: a failure at the end of the chain
    is attributed to researcher, the agent with no parent."""
    monitor = Monitor({"contract.txt": "The real clause."})
    monitor.check("researcher", [Claim("c_001", "invented clause", "contract.txt")])
    monitor.check(
        "editor",
        [Claim("c_002", "invented clause", "contract.txt", derived_from="c_001")],
    )

    result = monitor.check(
        "summarizer",
        [Claim("c_003", "invented clause", "contract.txt", derived_from="c_002")],
    )[0]

    assert result.reason == NOT_IN_SOURCE
    assert (result.origin_agent, result.origin_claim_id) == ("researcher", "c_001")


def test_new_claim_with_no_parent_originates_at_submitter():
    monitor = Monitor({"contract.txt": "The real clause."})

    result = monitor.check(
        "researcher", [Claim("c_001", "invented clause", "contract.txt")]
    )[0]

    assert result.reason == NOT_IN_SOURCE
    assert (result.origin_agent, result.origin_claim_id) == ("researcher", "c_001")


def test_missing_parent_reports_broken_lineage_with_last_known_agent():
    """Edge case 1: parent id never checked. BROKEN_LINEAGE, and the last
    known agent is named — never silently attributed to the submitter."""
    monitor = Monitor({"contract.txt": "The real clause."})

    result = monitor.check(
        "summarizer",
        [Claim("c_002", "real clause", "contract.txt", derived_from="missing")],
    )[0]

    assert result.reason == BROKEN_LINEAGE
    assert (result.origin_agent, result.origin_claim_id) == ("summarizer", "c_002")


def test_cycle_is_capped_and_reported_as_broken():
    """Edge case 2: the walk is capped at the number of recorded claims and
    reports the chain as broken on overrun."""
    monitor = Monitor({"contract.txt": "The real clause."})
    claims = [
        Claim("c_001", "real clause", "contract.txt", derived_from="c_002"),
        Claim("c_002", "real clause", "contract.txt", derived_from="c_001"),
    ]

    results = monitor.check("researcher", claims)

    assert all(result.reason == BROKEN_LINEAGE for result in results)
    assert all(result.origin_agent == "researcher" for result in results)


def test_reworded_quote_originates_at_the_child_not_the_parent():
    """Edge case 3: parent passed but child failed — the child altered the
    quote, so the child is the origin. This is the case that earns the name."""
    monitor = Monitor({"contract.txt": "The term is twelve months."})
    parent = monitor.check(
        "researcher", [Claim("c_001", "twelve months", "contract.txt")]
    )[0]

    child = monitor.check(
        "editor",
        [Claim("c_002", "twenty-four months", "contract.txt", derived_from="c_001")],
    )[0]

    assert parent.status == "PASSED"
    assert child.reason == NOT_IN_SOURCE
    assert (child.origin_agent, child.origin_claim_id) == ("editor", "c_002")
