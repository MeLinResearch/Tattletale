"""Origin tracing: the backward walk over ``derived_from`` (spec §6).

Build step 3. Lineage is a dictionary, not a graph engine (spec §2.4) — the
walk needs only the claims and results already recorded by the Monitor.
"""

from __future__ import annotations

from .models import Claim, ClaimResult


class BrokenLineageError(Exception):
    """Internal signal carrying the last claim whose submitter is known."""

    def __init__(self, agent: str, claim_id: str) -> None:
        super().__init__(f"Broken lineage after {agent} ({claim_id})")
        self.agent = agent
        self.claim_id = claim_id


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
    current_claim = claim
    current_result = results_by_id[claim.id]

    for _ in range(len(claims_by_id)):
        parent_id = current_claim.derived_from
        if parent_id is None:
            return current_result.agent, current_claim.id

        parent_claim = claims_by_id.get(parent_id)
        parent_result = results_by_id.get(parent_id)
        if parent_claim is None or parent_result is None:
            raise BrokenLineageError(current_result.agent, current_claim.id)

        if current_result.status == "FAILED" and parent_result.status == "PASSED":
            return current_result.agent, current_claim.id

        current_claim = parent_claim
        current_result = parent_result

    raise BrokenLineageError(current_result.agent, current_claim.id)
