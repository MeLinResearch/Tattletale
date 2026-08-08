"""Data model: Claim, ClaimResult, and reason codes (spec §3, §5.2)."""

from __future__ import annotations

from dataclasses import dataclass

# Reason codes (spec §5.2). A claim that passes gets no code; every failure
# gets exactly one.
NOT_IN_SOURCE = "NOT_IN_SOURCE"
UNKNOWN_SOURCE = "UNKNOWN_SOURCE"
EMPTY_QUOTE = "EMPTY_QUOTE"
BROKEN_LINEAGE = "BROKEN_LINEAGE"

REASON_CODES = frozenset({NOT_IN_SOURCE, UNKNOWN_SOURCE, EMPTY_QUOTE, BROKEN_LINEAGE})

PASSED = "PASSED"
FAILED = "FAILED"


@dataclass(frozen=True)
class Claim:
    """A structured claim submitted to ``Monitor.check`` (spec §3).

    ``derived_from`` is what makes origin tracing possible: an agent that
    carries a claim forward reuses the upstream id; an agent that states
    something new leaves it ``None`` and owns the claim.
    """

    id: str
    """Unique within a run."""

    text: str
    """The quoted span."""

    source: str
    """Name of the loaded document the quote claims to be from."""

    derived_from: str | None = None
    """Id of the upstream claim, if this claim was carried forward."""


@dataclass(frozen=True)
class ClaimResult:
    """The verdict for one checked claim (spec §3).

    ``status`` is ``PASSED`` or ``FAILED`` — binary, never a score (spec §2.1).
    """

    claim_id: str
    agent: str
    """The agent that submitted the claim to ``check``."""

    status: str
    """``PASSED`` | ``FAILED``."""

    reason: str | None = None
    """One reason code from :data:`REASON_CODES` on failure, ``None`` on pass."""

    origin_agent: str | None = None
    """First agent in the lineage chain (spec §6)."""

    origin_claim_id: str | None = None
    """Id of the claim at the root of the lineage chain."""
