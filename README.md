# Tattletale

Origin tracing for agent-generated claims. Tattletale verifies **quotation,
not correctness**: it checks that a quoted span actually appears in the source
document, and when it doesn't, it names the agent that first introduced it —
not just the agent that last repeated it.

> **Status: v0.1 implementation complete.** The deterministic checker, lineage
> tracing, text and JSON reports, quote helper, demo, and adversarial suite are
> implemented against the frozen [architecture](ARCHITECTURE.md).

## Why

In a multi-agent pipeline, agent A produces a claim with a supporting quote.
Agent B carries it forward. Agent C summarizes B. By the time a fabricated
quote reaches the user, three agents have handled it and none of them checked
whether the quote exists in the source. Tattletale answers one question
mechanically: does this quote appear in the source, and if not, which agent
invented it.

## What it looks like

```python
from tattletale import Claim, Monitor

tt = Monitor({"contract.pdf": contract_text})

tt.check(
    agent="researcher",
    claims=[Claim("c_001", "renews every 12 months", "contract.pdf")],
)

print(tt.report())
```

```
TATTLETALE    8 claims     3 failed
source: contract.pdf       sha256:4f1a... (normalized)

summarizer          3 claims     2 FAILED
  c_004     "renews automatically every 24 months"
            NOT_IN_SOURCE
            inherited from: researcher (c_001)
...
```

Three methods — `Monitor(sources)`, `check(agent, claims)`,
`report(format="text")` — are the whole library.

Use `report(format="json")` for a deterministic machine-readable record. It
contains summary counts, normalized source hashes, per-agent counts, and every
passing and failing claim with lineage fields.

For unstructured messages, the optional helper
`tattletale.extract.quoted_spans(message, source)` creates deterministic
`Claim` objects from straight or curly double-quoted spans. It is deliberately
best-effort and never participates in verdicts.

## Design in one breath

- The check is **binary**. A quote is in the normalized source or it is not.
  No similarity scores, no thresholds.
- **Normalize once, compare exactly.** Deterministic cleanup at load time
  (whitespace collapse, quote straightening, soft-hyphen repair, NFKC), never
  fuzzy matching at compare time.
- **Lineage is a dictionary.** Each claim may carry `derived_from`; the
  report walks that chain backward to name the origin agent.
- **No model calls, no dependencies, no persistence.** Arithmetic and string
  comparison only.

Full design, data model, reason codes, and edge cases:
[ARCHITECTURE.md](ARCHITECTURE.md).

## Development

```bash
make setup   # editable install with dev extras
make test    # pytest
make demo    # runnable 3-agent pipeline with a planted fabrication
```

Requires Python 3.10+ (developed on 3.12). The library itself has zero
runtime dependencies.

## Repository layout

```
src/tattletale/
  models.py      # Claim / ClaimResult, reason codes       (spec §3, §5.2)
  normalize.py   # deterministic normalization + hashing   (spec §5.1)
  monitor.py     # Monitor: the three-method API           (spec §4)
  lineage.py     # origin walk and its three edge cases    (spec §6)
  report.py      # text and JSON renderers                 (spec §7)
  extract.py     # optional best-effort quote extractor    (spec §4)
tests/           # one file per build step; adversarial suite is step 8
demo/            # 3-agent pipeline with a planted fabrication (spec §10)
```

## License

[MIT](LICENSE)
