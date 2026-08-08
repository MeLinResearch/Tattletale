"""Deterministic text normalization and source hashing (spec §5.1).

Build step 1. Applied identically to source text at load time and to every
claim quote at check time — that symmetry is the whole trick.
"""

from __future__ import annotations


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
    raise NotImplementedError("Build step 1: normalizer (spec §5.1)")


def source_hash(normalized_text: str) -> str:
    """SHA-256 hex digest of an already-normalized source (spec §5.1).

    Computed at load time; surfaced in the report header so a reader can
    confirm which version of the source the verdicts refer to.
    """
    raise NotImplementedError("Build step 1: source hashing (spec §5.1)")
