"""Optional best-effort claim extraction (spec §4). Build step 6.

Shipped separately from the checker on purpose: extracting claims from free
text is a guess, and guessing never belongs in the checker (spec §2.3). This
helper will miss things. It never affects a verdict.
"""

from __future__ import annotations

from .models import Claim


def quoted_spans(message: str, source: str) -> list[Claim]:
    """Pull anything inside quotation marks out of ``message`` as Claims.

    Best-effort by design: a missed claim is an acceptable failure here.
    Returned claims have generated ids, the given ``source``, and no
    ``derived_from`` — lineage is the caller's knowledge, not this helper's.
    """
    raise NotImplementedError("Build step 6: quoted_spans (spec §4)")
