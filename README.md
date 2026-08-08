# Tattletale

Origin tracing for agent-generated claims. Tattletale verifies **quotation,
not correctness**: it checks that a quoted span actually appears in the source
document, and when it doesn't, it names the agent that first introduced it —
not just the agent that last repeated it.

> **Status: scaffolding.** The structure, data model, and tests are laid out;
> the implementation follows the build order in
> [ARCHITECTURE.md](ARCHITECTURE.md). See [AGENTS.md](AGENTS.md) if you are an
> agent working on this repo.

## Why

In a multi-agent pipeline, agent A produces a claim with a supporting quote.
Agent B carries it forward. Agent C summarizes B. By the time a fabricated
quote reaches the user, three agents have handled it and none of them checked
whether the quote exists in the source. Tattletale answers one question
mechanically: does this quote appear in the source, and if not, which agent
invented it.

## What it looks like

```python
from tattletale import Monitor

tt = Monitor({"contract.pdf": contract_text})

tt.check(agent="researcher", claims=[...])
tt.check(agent="summarizer", claims=[...])

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
make demo    # 3-agent pipeline demo (build step 7)
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
