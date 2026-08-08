"""Build step 6: the best-effort ``quoted_spans`` helper (spec §4).

Un-skip and complete these when implementing ``tattletale.extract``. A missed
claim is acceptable here; a wrong verdict is not — the helper never affects
verdicts.
"""

import pytest

STEP_6 = pytest.mark.skip(reason="Build step 6 not implemented: quoted_spans (spec §4)")


@STEP_6
def test_extracts_double_quoted_spans_as_claims():
    ...


@STEP_6
def test_extracted_claims_carry_the_given_source_and_no_lineage():
    ...


@STEP_6
def test_message_without_quotes_yields_no_claims():
    ...
