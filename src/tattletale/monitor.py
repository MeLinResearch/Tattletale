"""Monitor: the three-method API surface (spec §4).

Build step 2 (``check`` with reason codes), then steps 3-5 layer in lineage
and the report renderers. A Monitor lives for one run — no persistence
(spec §8).
"""

from __future__ import annotations

from dataclasses import replace

from .lineage import BrokenLineageError, find_origin
from .models import (
    BROKEN_LINEAGE,
    EMPTY_QUOTE,
    FAILED,
    NOT_IN_SOURCE,
    PASSED,
    UNKNOWN_SOURCE,
    Claim,
    ClaimResult,
)
from .normalize import normalize, source_hash
from .report import render_json, render_text


class Monitor:
    """Checks structured claims against normalized source documents.

    ::

        tt = Monitor({"contract.pdf": contract_text})
        tt.check(agent="researcher", claims=[...])
        print(tt.report())
    """

    def __init__(self, sources: dict[str, str]) -> None:
        """Load and normalize source text (spec §4).

        ``sources`` maps document name to raw text. Each source is normalized
        (spec §5.1) and hashed exactly once, here.
        """
        self._sources: dict[str, str] = {}
        self._source_hashes: dict[str, str] = {}
        for name, text in sources.items():
            normalized = normalize(text)
            self._sources[name] = normalized
            self._source_hashes[name] = source_hash(normalized)

        self._claims: dict[str, tuple[str, Claim]] = {}
        self._results: list[ClaimResult] = []
        self._agents: list[str] = []

    def check(self, agent: str, claims: list[Claim]) -> list[ClaimResult]:
        """Validate each claim, record the result, return the result list.

        Verdicts are binary (spec §2.1). Failure reasons are the four codes
        in spec §5.2; origin attribution follows the lineage walk in spec §6
        (build step 3).
        """
        if agent not in self._agents:
            self._agents.append(agent)

        provisional_results: list[ClaimResult] = []

        for claim in claims:
            quote = normalize(claim.text)
            if not quote:
                status, reason = FAILED, EMPTY_QUOTE
            elif claim.source not in self._sources:
                status, reason = FAILED, UNKNOWN_SOURCE
            elif quote not in self._sources[claim.source]:
                status, reason = FAILED, NOT_IN_SOURCE
            else:
                status, reason = PASSED, None

            result = ClaimResult(
                claim_id=claim.id,
                agent=agent,
                status=status,
                reason=reason,
            )
            self._claims[claim.id] = (agent, claim)
            provisional_results.append(result)

        claims_by_id = {
            claim_id: recorded_claim
            for claim_id, (_, recorded_claim) in self._claims.items()
        }
        results_by_id = {
            result.claim_id: result for result in self._results + provisional_results
        }
        batch_results: list[ClaimResult] = []

        for claim, result in zip(claims, provisional_results):
            if result.status == FAILED or claim.derived_from is not None:
                try:
                    origin_agent, origin_claim_id = find_origin(
                        claim, claims_by_id, results_by_id
                    )
                except BrokenLineageError as broken:
                    result = replace(
                        result,
                        status=FAILED,
                        reason=BROKEN_LINEAGE,
                        origin_agent=broken.agent,
                        origin_claim_id=broken.claim_id,
                    )
                else:
                    if result.status == FAILED:
                        result = replace(
                            result,
                            origin_agent=origin_agent,
                            origin_claim_id=origin_claim_id,
                        )

            batch_results.append(result)

        self._results.extend(batch_results)

        return batch_results

    def report(self, format: str = "text") -> str:
        """Render accumulated results as ``text`` (step 4) or ``json`` (step 5).

        The text layout is specified in spec §7 and is the product — agents
        with zero failures still appear. JSON carries the same content plus
        the source hash and every passing claim.
        """
        if format == "text":
            claims_by_id = {
                claim_id: claim for claim_id, (_, claim) in self._claims.items()
            }
            return render_text(
                self._results,
                self._source_hashes,
                claims_by_id,
                self._agents,
            )
        if format == "json":
            claims_by_id = {
                claim_id: claim for claim_id, (_, claim) in self._claims.items()
            }
            return render_json(
                self._results,
                self._source_hashes,
                claims_by_id,
                self._agents,
            )
        raise ValueError("format must be 'text' or 'json'")
