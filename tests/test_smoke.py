"""Scaffold smoke test: the package imports and the data model holds.

This is the only test that runs before build step 1 lands. It keeps CI green
on the bare scaffold and pins the public API surface.
"""

import tattletale
from tattletale import Claim, ClaimResult


def test_public_api_surface():
    expected = {
        "Monitor",
        "Claim",
        "ClaimResult",
        "NOT_IN_SOURCE",
        "UNKNOWN_SOURCE",
        "EMPTY_QUOTE",
        "BROKEN_LINEAGE",
    }
    assert set(tattletale.__all__) == expected
    for name in expected:
        assert hasattr(tattletale, name)


def test_claim_defaults():
    claim = Claim(id="c_001", text="renews automatically", source="contract.pdf")
    assert claim.derived_from is None


def test_claim_result_defaults():
    result = ClaimResult(claim_id="c_001", agent="researcher", status="PASSED")
    assert result.reason is None
    assert result.origin_agent is None
    assert result.origin_claim_id is None
