"""Deterministic text normalization and source hashing (spec §5.1).

Build step 1. Applied identically to source text at load time and to every
claim quote at check time — that symmetry is the whole trick.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata


_CURLY_QUOTES = str.maketrans({
    "\u201c": '"',
    "\u201d": '"',
    "\u2018": "'",
    "\u2019": "'",
})
_LINE_BREAK_HYPHENATION = re.compile(r"-[ \t\f\v]*(?:\r\n|\r|\n)[ \t\f\v]*")


def normalize(text: str) -> str:
    """Normalize ``text`` with exactly the five rules from spec §5.1.

    1. Collapse all runs of whitespace to a single space.
    2. Straighten curly quotes and apostrophes to ASCII.
    3. Remove soft hyphens and join words broken across line breaks.
    4. Normalize unicode to NFKC.
    5. Strip leading and trailing whitespace.

    Nothing else: no case folding, no punctuation stripping, no stemming.
    Every rule must be reversible in the reader's head (spec §5.1).
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_CURLY_QUOTES)
    text = text.replace("\u00ad", "")
    text = _LINE_BREAK_HYPHENATION.sub("", text)
    return " ".join(text.split())


def source_hash(normalized_text: str) -> str:
    """SHA-256 hex digest of an already-normalized source (spec §5.1).

    Computed at load time; surfaced in the report header so a reader can
    confirm which version of the source the verdicts refer to.
    """
    return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
