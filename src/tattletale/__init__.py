"""Tattletale: origin tracing for agent-generated claims.

Verifies quotation, not correctness. See ARCHITECTURE.md for the spec.
"""

from .models import (
    BROKEN_LINEAGE,
    EMPTY_QUOTE,
    NOT_IN_SOURCE,
    UNKNOWN_SOURCE,
    Claim,
    ClaimResult,
)
from .monitor import Monitor

__version__ = "0.1.0.dev0"

__all__ = [
    "Monitor",
    "Claim",
    "ClaimResult",
    "NOT_IN_SOURCE",
    "UNKNOWN_SOURCE",
    "EMPTY_QUOTE",
    "BROKEN_LINEAGE",
]
