"""Build step 6: the best-effort ``quoted_spans`` helper (spec §4).

Un-skip and complete these when implementing ``tattletale.extract``. A missed
claim is acceptable here; a wrong verdict is not — the helper never affects
verdicts.
"""

from tattletale.extract import quoted_spans


def test_extracts_double_quoted_spans_as_claims():
    claims = quoted_spans('One "alpha" and one “beta”.', source="contract.txt")

    assert [claim.id for claim in claims] == ["c_001", "c_002"]
    assert [claim.text for claim in claims] == ["alpha", "beta"]


def test_extracted_claims_carry_the_given_source_and_no_lineage():
    claims = quoted_spans('The message says "real clause".', source="contract.txt")

    assert len(claims) == 1
    assert claims[0].source == "contract.txt"
    assert claims[0].derived_from is None


def test_message_without_quotes_yields_no_claims():
    assert quoted_spans("No quoted spans here.", source="contract.txt") == []
