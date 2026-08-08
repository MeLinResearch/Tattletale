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


def main() -> int:
    print("Tattletale demo is build step 7 and is not implemented yet.")
    print("See the module docstring and ARCHITECTURE.md §10 for the script.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
