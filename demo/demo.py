"""Build step 7: the demo (spec §10). Three agents, one document, one
planted fabrication.

The pipeline to implement:

- ``researcher`` reads ``demo/contract.txt`` and returns four real quotes
  and one invented clause ("renews automatically every 24 months" — the
  contract says 12).
- ``editor`` passes all five forward unchanged, reusing the upstream claim
  ids via ``derived_from``.
- ``summarizer`` carries three of them, including the invented one, into a
  final summary.

The final output looks clean. Tattletale names ``researcher``. Under thirty
seconds of terminal recording — that is the artifact.

Once this runs, wire ``make demo`` into CI (.github/workflows/ci.yml).
"""

import sys
from pathlib import Path

from tattletale import Claim, Monitor


def _forward(claims: list[Claim], start: int) -> list[Claim]:
    """Carry claims forward with new ids and explicit parent links."""
    return [
        Claim(
            id=f"c_{start + offset:03d}",
            text=claim.text,
            source=claim.source,
            derived_from=claim.id,
        )
        for offset, claim in enumerate(claims)
    ]


def main() -> int:
    contract_path = Path(__file__).with_name("contract.txt")
    with contract_path.open(encoding="utf-8") as contract_file:
        monitor = Monitor({"contract.txt": contract_file.read()})

    researcher_claims = [
        Claim("c_001", "renews automatically every 12 months", "contract.txt"),
        Claim("c_002", "monthly service fee of $4,500", "contract.txt"),
        Claim("c_003", "no less than reasonable care", "contract.txt"),
        Claim("c_004", "liability shall exceed the fees paid", "contract.txt"),
        Claim("c_005", "renews automatically every 24 months", "contract.txt"),
    ]
    monitor.check("researcher", researcher_claims)

    editor_claims = _forward(researcher_claims, start=6)
    monitor.check("editor", editor_claims)

    summarizer_claims = _forward(
        [editor_claims[0], editor_claims[3], editor_claims[4]], start=11
    )
    summary_results = monitor.check("summarizer", summarizer_claims)

    planted = summary_results[-1]
    if planted.origin_agent != "researcher" or planted.origin_claim_id != "c_005":
        raise RuntimeError("demo invariant failed: planted fabrication origin was not found")

    print(monitor.report())
    return 0


if __name__ == "__main__":
    sys.exit(main())
