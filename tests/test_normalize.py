"""Build step 1: the normalizer (spec §5.1).

Un-skip and complete these when implementing ``tattletale.normalize``. The
step proves messy input normalizes predictably and identically on both sides
(source at load, quote at check).
"""

import pytest

STEP_1 = pytest.mark.skip(reason="Build step 1 not implemented: normalizer (spec §5.1)")


@STEP_1
def test_collapses_whitespace_runs_to_single_space():
    ...


@STEP_1
def test_straightens_curly_quotes_and_apostrophes():
    ...


@STEP_1
def test_removes_soft_hyphens_and_joins_line_break_hyphenation():
    ...


@STEP_1
def test_applies_nfkc_unicode_normalization():
    ...


@STEP_1
def test_strips_leading_and_trailing_whitespace():
    ...


@STEP_1
def test_does_not_case_fold_or_strip_punctuation():
    """Nothing beyond the five rules — no case folding, no punctuation
    stripping, no stemming (spec §5.1)."""
    ...


@STEP_1
def test_is_idempotent():
    """normalize(normalize(x)) == normalize(x) — determinism is the product."""
    ...


@STEP_1
def test_source_hash_is_sha256_of_normalized_text():
    ...
