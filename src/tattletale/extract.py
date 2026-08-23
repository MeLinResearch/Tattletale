"""Optional best-effort claim extraction (spec §4). Build step 6.

Shipped separately from the checker on purpose: extracting claims from free
text is a guess, and guessing never belongs in the checker (spec §2.3). This
helper will miss things. It never affects a verdict.
"""

from __future__ import annotations

import re

from .models import Claim


_QUOTED_SPAN = re.compile(r'"([^"\n]+)"|“([^”\n]+)”')


def quoted_spans(message: str, source: str) -> list[Claim]:
    """Pull anything inside quotation marks out of ``message`` as Claims.

    Best-effort by design: a missed claim is an acceptable failure here.
    Returned claims have generated ids, the given ``source``, and no
    ``derived_from`` — lineage is the caller's knowledge, not this helper's.
    """
    claims = []
    for index, match in enumerate(_QUOTED_SPAN.finditer(message), start=1):
        text = match.group(1) if match.group(1) is not None else match.group(2)
        claims.append(
            Claim(
                id=f"c_{index:03d}",
                text=text,
                source=source,
            )
        )
    return claims
