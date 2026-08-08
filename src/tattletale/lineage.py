"""Origin tracing: the backward walk over ``derived_from`` (spec §6).

Build step 3. Lineage is a dictionary, not a graph engine (spec §2.4) — the
walk needs only the claims and results already recorded by the Monitor.
"""

from __future__ import annotations

from .models import Claim, ClaimResult


def find_origin(
    claim: Claim,
    claims_by_id: dict[str, Claim],
    results_by_id: dict[str, ClaimResult],
) -> tuple[str, str]:
    """Walk ``derived_from`` backward and return ``(origin_agent, origin_claim_id)``.

    Three cases the walk must handle (spec §6):

    1. **Parent not found.** Report ``BROKEN_LINEAGE`` and name the last
       known agent. Never silently attribute to the submitter.
    2. **Cycle.** Cap the walk at the number of recorded claims; on overrun,
       stop and report the chain as broken.
    3. **Parent passed but child failed.** The child altered the quote, so
       the origin is the child, not the parent. A modified quote is a new
       claim. (This case is the one that earns the name.)
    """
    raise NotImplementedError("Build step 3: lineage walk (spec §6)")
