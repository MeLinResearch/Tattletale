# Agent Instructions

You are implementing Tattletale, a small deterministic Python library.
[ARCHITECTURE.md](ARCHITECTURE.md) is the authoritative spec — section
references below (§) point into it. When this file and the spec disagree, the
spec wins.

## Hard rules

These come from the spec's principles (§2) and non-goals (§8). Do not trade
them away for convenience:

1. **Binary verdicts only.** No similarity scores, thresholds, or confidence
   values anywhere in the codebase.
2. **Exactly the five normalization rules in §5.1.** No case folding, no
   punctuation stripping, no stemming. Same input must produce the same
   verdict on every machine.
3. **Zero runtime dependencies.** Standard library only. No LLM calls, no
   embeddings, no network.
4. **No persistence, no framework adapters, no orchestration.** A `Monitor`
   lives for one run.
5. **A wrong verdict is never acceptable.** A missed claim (in the optional
   extractor) is. Never let `tattletale.extract` influence a verdict.

## Where things go

| File                        | Owns                                          | Spec  |
| --------------------------- | --------------------------------------------- | ----- |
| `src/tattletale/models.py`  | `Claim`, `ClaimResult`, reason codes          | §3, §5.2 |
| `src/tattletale/normalize.py` | `normalize()`, `source_hash()`              | §5.1  |
| `src/tattletale/monitor.py` | `Monitor.__init__ / check / report`           | §4    |
| `src/tattletale/lineage.py` | origin walk, three edge cases                 | §6    |
| `src/tattletale/report.py`  | text renderer, JSON renderer                  | §7    |
| `src/tattletale/extract.py` | `quoted_spans()` best-effort helper           | §4    |
| `demo/demo.py`              | 3-agent pipeline, planted fabrication         | §10   |

Public API is re-exported from `src/tattletale/__init__.py` and is exactly:
`Monitor`, `Claim`, `ClaimResult`, and the four reason-code constants.

## Build order

Work the steps in sequence (§9). Each step has a test file with skipped
placeholder tests: implementing a step means **un-skipping and completing its
tests**, then making them pass. Do not implement ahead of the tests.

- [x] Step 1 — normalizer (`tests/test_normalize.py`)
- [x] Step 2 — `Monitor.check` + reason codes, no lineage (`tests/test_check.py`)
- [x] Step 3 — lineage walk, three edge cases (`tests/test_lineage.py`)
- [x] Step 4 — text report (`tests/test_report.py`)
- [ ] Step 5 — JSON report (`tests/test_report.py`)
- [ ] Step 6 — `extract.quoted_spans` (`tests/test_extract.py`)
- [ ] Step 7 — demo pipeline (`demo/demo.py`, then wire `make demo` into CI)
- [ ] Step 8 — adversarial suite (`tests/test_adversarial.py`)

Check items off in this file as you complete them, in the same commit as the
implementation.

## Checks

After changing code, run:

```bash
make test
```

That runs pytest over `tests/`. CI runs the same target — keep it green on
every commit. `make demo` must run clean once step 7 lands.

## Style

- Python 3.10+ syntax; the repo develops on 3.12 (`.python-version`).
- Standard library only, `dataclasses` for the data model.
- Keep docstrings pointing at spec sections the way the stubs already do.
- Small modules, no clever indirection — the whole library is three methods.
