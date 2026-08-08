"""Report renderers (spec §7). The report is the product.

Build step 4 (text) and step 5 (JSON). Both render the same accumulated
results; JSON additionally carries the source hash and every passing claim,
in a stable shape for machine consumers.
"""

from __future__ import annotations

from .models import ClaimResult


def render_text(
    results: list[ClaimResult],
    source_hashes: dict[str, str],
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
    raise NotImplementedError("Build step 4: text report (spec §7)")


def render_json(
    results: list[ClaimResult],
    source_hashes: dict[str, str],
) -> str:
    """Render the JSON report (spec §7): same content as text, plus the
    source hash and every passing claim. The shape is a public contract —
    once step 5 lands, changing it is a breaking change.
    """
    raise NotImplementedError("Build step 5: JSON report (spec §7)")
