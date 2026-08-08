"""Monitor: the three-method API surface (spec §4).

Build step 2 (``check`` with reason codes), then steps 3-5 layer in lineage
and the report renderers. A Monitor lives for one run — no persistence
(spec §8).
"""

from __future__ import annotations

from .models import Claim, ClaimResult


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
        raise NotImplementedError("Build step 2: Monitor (spec §4)")

    def check(self, agent: str, claims: list[Claim]) -> list[ClaimResult]:
        """Validate each claim, record the result, return the result list.

        Verdicts are binary (spec §2.1). Failure reasons are the four codes
        in spec §5.2; origin attribution follows the lineage walk in spec §6
        (build step 3).
        """
        raise NotImplementedError("Build step 2: Monitor.check (spec §4, §5)")

    def report(self, format: str = "text") -> str:
        """Render accumulated results as ``text`` (step 4) or ``json`` (step 5).

        The text layout is specified in spec §7 and is the product — agents
        with zero failures still appear. JSON carries the same content plus
        the source hash and every passing claim.
        """
        raise NotImplementedError("Build steps 4-5: report (spec §7)")
