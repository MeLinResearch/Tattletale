"""Build step 1: the normalizer (spec §5.1).

The normalizer is deliberately symmetrical: source text and claim text use
the exact same function, so their comparison is predictable.
"""

import hashlib

from tattletale.normalize import normalize, source_hash


def test_collapses_ordinary_whitespace_runs_to_one_space():
    assert normalize("one   two    three") == "one two three"


def test_tabs_and_newlines_normalize_as_whitespace():
    assert normalize("one\ttwo\nthree\r\nfour") == "one two three four"


def test_strips_leading_and_trailing_whitespace():
    assert normalize("  \n  quote text\t ") == "quote text"


def test_straightens_curly_double_quotes_and_apostrophes():
    assert normalize("\u201cAda\u2019s report\u201d") == '"Ada\'s report"'


def test_removes_soft_hyphens():
    assert normalize("re\u00adnewal") == "renewal"


def test_joins_words_broken_across_line_breaks_by_hyphenation():
    assert normalize("auto-\nmatically") == "automatically"


def test_applies_nfkc_unicode_normalization():
    assert normalize("\uff21\uff22\uff23 \u2460") == "ABC 1"


def test_is_deterministic_and_idempotent():
    raw = "  \u201cFull-\nwidth\u00ad\uff21\u201d\t"
    first = normalize(raw)

    assert normalize(raw) == first
    assert normalize(first) == first


def test_does_not_case_fold_or_strip_punctuation():
    assert normalize("Case-Sensitive: Yes!") == "Case-Sensitive: Yes!"


def test_same_normalizer_produces_identical_source_and_claim_text():
    source_text = "The \u201cservice-\nterm\u201d\u00a0is 12 months."
    claim_text = 'The "serviceterm" is 12 months.'

    assert normalize(source_text) == normalize(claim_text)


def test_source_hash_is_sha256_of_normalized_text():
    normalized = normalize("  source\ntext  ")

    assert source_hash(normalized) == hashlib.sha256(b"source text").hexdigest()
