"""Report renderers (spec §7). The report is the product.

Build step 4 (text) and step 5 (JSON). Both render the same accumulated
results; JSON additionally carries the source hash and every passing claim,
in a stable shape for machine consumers.
"""

from __future__ import annotations

import json

from .models import BROKEN_LINEAGE, FAILED, Claim, ClaimResult
from .normalize import normalize


def render_text(
    results: list[ClaimResult],
    source_hashes: dict[str, str],
    claims_by_id: dict[str, Claim],
    agents: list[str],
) -> str:
    """Render the text report specified in spec §7.

    Layout requirements:
    - header line with total claim and failure counts
    - one ``source: <name>  sha256:<hash> (normalized)`` line per source
    - one block per agent with per-agent counts, failed claims listed with
      quote, reason, and origin (``originated here`` vs
      ``inherited from: <agent> (<claim_id>)``)
    - agents with zero failures (or zero claims) still appear
    """
    failed = sum(result.status == FAILED for result in results)
    lines = [f"TATTLETALE    {len(results)} claims     {failed} failed"]

    for name, digest in source_hashes.items():
        lines.append(f"source: {name}       sha256:{digest} (normalized)")

    for agent in agents:
        agent_results = [result for result in results if result.agent == agent]
        agent_failed = [result for result in agent_results if result.status == FAILED]
        lines.extend(
            [
                "",
                f"{agent}          {len(agent_results)} claims     "
                f"{len(agent_failed)} FAILED",
            ]
        )

        for result in agent_failed:
            claim = claims_by_id[result.claim_id]
            lines.extend(
                [
                    f'  {result.claim_id}     "{normalize(claim.text)}"',
                    f"            {result.reason}",
                ]
            )
            if result.reason == BROKEN_LINEAGE:
                lines.append(
                    "            lineage broken after: "
                    f"{result.origin_agent} ({result.origin_claim_id})"
                )
            elif (
                result.origin_agent == result.agent
                and result.origin_claim_id == result.claim_id
            ):
                lines.append("            originated here")
            else:
                lines.append(
                    "            inherited from: "
                    f"{result.origin_agent} ({result.origin_claim_id})"
                )

    return "\n".join(lines)


def render_json(
    results: list[ClaimResult],
    source_hashes: dict[str, str],
    claims_by_id: dict[str, Claim],
    agents: list[str],
) -> str:
    """Render the JSON report (spec §7): same content as text, plus the
    source hash and every passing claim. The shape is a public contract —
    once step 5 lands, changing it is a breaking change.
    """
    failed = sum(result.status == FAILED for result in results)
    payload = {
        "summary": {"claims": len(results), "failed": failed},
        "sources": {
            name: {"sha256": digest, "normalized": True}
            for name, digest in source_hashes.items()
        },
        "agents": [
            {
                "agent": agent,
                "claims": sum(result.agent == agent for result in results),
                "failed": sum(
                    result.agent == agent and result.status == FAILED
                    for result in results
                ),
            }
            for agent in agents
        ],
        "results": [],
    }

    for result in results:
        claim = claims_by_id[result.claim_id]
        payload["results"].append(
            {
                "claim_id": result.claim_id,
                "agent": result.agent,
                "status": result.status,
                "reason": result.reason,
                "source": claim.source,
                "quote": normalize(claim.text),
                "derived_from": claim.derived_from,
                "origin_agent": result.origin_agent,
                "origin_claim_id": result.origin_claim_id,
            }
        )

    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
