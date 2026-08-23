"""Build step 2: ``Monitor.check`` with reason codes, no lineage (spec §4, §5).

Un-skip and complete these when implementing ``tattletale.monitor``. The step
proves fabricated quotes are rejected — every verdict binary, every failure
carrying exactly one reason code.
"""

from tattletale import EMPTY_QUOTE, NOT_IN_SOURCE, UNKNOWN_SOURCE, Claim, Monitor


def test_exact_quote_passes():
    monitor = Monitor({"contract.txt": "The term is twelve months."})

    result = monitor.check(
        agent="researcher",
        claims=[Claim(id="c_001", text="term is twelve months", source="contract.txt")],
    )[0]

    assert result.status == "PASSED"
    assert result.reason is None


def test_fabricated_quote_fails_not_in_source():
    monitor = Monitor({"contract.txt": "The term is twelve months."})

    result = monitor.check(
        agent="researcher",
        claims=[Claim(id="c_001", text="term is twenty-four months", source="contract.txt")],
    )[0]

    assert result.status == "FAILED"
    assert result.reason == NOT_IN_SOURCE


def test_quote_present_after_normalization_passes():
    """A curly-quoted claim against a straight-quoted source still passes —
    both sides normalize identically (spec §5.1)."""
    monitor = Monitor({"contract.txt": 'The agreement calls it "Ada\'s service".'})

    result = monitor.check(
        agent="researcher",
        claims=[Claim(id="c_001", text="  “Ada’s\nservice”  ", source="contract.txt")],
    )[0]

    assert result.status == "PASSED"
    assert result.reason is None


def test_unloaded_document_fails_unknown_source():
    monitor = Monitor({"contract.txt": "A loaded source."})

    result = monitor.check(
        agent="researcher",
        claims=[Claim(id="c_001", text="A quote", source="missing.txt")],
    )[0]

    assert result.status == "FAILED"
    assert result.reason == UNKNOWN_SOURCE


def test_whitespace_only_quote_fails_empty_quote():
    monitor = Monitor({"contract.txt": "A loaded source."})

    result = monitor.check(
        agent="researcher",
        claims=[Claim(id="c_001", text=" \t\n\r ", source="missing.txt")],
    )[0]

    assert result.status == "FAILED"
    assert result.reason == EMPTY_QUOTE


def test_passing_claim_has_no_reason_code():
    """A claim that passes gets no code; every failure gets exactly one
    (spec §5.2)."""
    monitor = Monitor({"contract.txt": "alpha beta gamma"})
    claims = [
        Claim(id="c_001", text="alpha", source="contract.txt"),
        Claim(id="c_002", text="beta gamma", source="contract.txt"),
    ]

    results = monitor.check(agent="researcher", claims=claims)

    assert all(result.status == "PASSED" for result in results)
    assert all(result.reason is None for result in results)


def test_check_returns_results_and_records_them():
    """check() returns the result list for the batch and accumulates results
    for report() (spec §4)."""
    monitor = Monitor({"contract.txt": "alpha beta"})
    first_claim = Claim(id="c_001", text="alpha", source="contract.txt")
    second_claim = Claim(id="c_002", text="fabricated", source="contract.txt")

    first_batch = monitor.check(agent="researcher", claims=[first_claim])
    second_batch = monitor.check(agent="editor", claims=[second_claim])

    assert [result.claim_id for result in first_batch] == ["c_001"]
    assert [result.claim_id for result in second_batch] == ["c_002"]
    assert monitor._results == first_batch + second_batch
    assert monitor._claims == {
        "c_001": ("researcher", first_claim),
        "c_002": ("editor", second_claim),
    }
