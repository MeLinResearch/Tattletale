# Tattletale — Architecture

Origin tracing for agent-generated claims.

> When a quote is wrong, you learn which agent **first said it**, not just
> which agent last repeated it.

- **Status:** Draft v0.1
- **Scope:** One library. Not a framework, not a mesh, not an eval suite.
- **License:** MIT, intended for public release.

---

## 1. The problem

In a multi-agent pipeline, agent A produces a claim with a supporting quote.
Agent B reads A's output and carries the claim forward. Agent C summarizes B.
By the time a wrong quote reaches the user, three agents have handled it and
none of them checked whether the quote exists in the source.

Existing tooling records outputs. It does not record where a claim came from.
Debugging "who invented this clause?" is currently a manual read of the
transcript.

Tattletale answers one question mechanically: does this quote appear in the
source document, and if not, which agent introduced it.

## 2. Principles

1. **The check is binary.** A quote either appears in the normalized source or
   it does not. No similarity score, no threshold, no tunable confidence. A
   result nobody can negotiate with is the entire value proposition.
2. **Normalize once, compare exactly.** Documents are messy. The fix is
   deterministic cleanup at load time, not fuzzy matching at compare time.
   Same input yields the same verdict on every run, on every machine.
3. **The core takes structured claims.** Extracting claims from free text is a
   guess. Guessing belongs in an optional helper, never in the checker. A
   missed claim is an acceptable failure. A wrong verdict is not.
4. **Lineage is a dictionary, not a graph engine.** Each claim knows the id of
   the claim it came from. The report walks that chain backward. No graph
   library, no bus, no persistence layer.

## 3. Data model

### Claim (input)

```python
Claim(
    id="c_004",                                # unique within a run
    text="renews automatically every 24 months",  # the quoted span
    source="contract.pdf",                     # which loaded document it claims to be from
    derived_from="c_001",                      # optional: id of the upstream claim
)
```

`derived_from` is what makes origin tracing possible. An agent that carries a
claim forward reuses the upstream id. An agent that states something new
leaves it null and owns the claim.

### ClaimResult (output)

```python
ClaimResult(
    claim_id="c_004",
    agent="summarizer",          # who submitted it
    status="FAILED",             # PASSED | FAILED
    reason="NOT_IN_SOURCE",      # reason code, see 5.2
    origin_agent="researcher",   # first agent in the lineage chain
    origin_claim_id="c_001",
)
```

## 4. API surface

Three methods. That is the whole library.

```python
from tattletale import Monitor

tt = Monitor({"contract.pdf": contract_text})

tt.check(agent="researcher", claims=[...])
tt.check(agent="summarizer", claims=[...])

print(tt.report())
```

| Method                 | Does                                                              |
| ---------------------- | ----------------------------------------------------------------- |
| `Monitor(sources)`     | Loads and normalizes source text. Dict of name to string.         |
| `check(agent, claims)` | Validates each claim, records the result, returns the result list. |
| `report(format="text")`| Renders accumulated results. `text` or `json`.                    |

Optional convenience, shipped separately and clearly labeled as best-effort:

```python
from tattletale.extract import quoted_spans

claims = quoted_spans(agent_message, source="contract.pdf")
```

It pulls anything inside quotation marks. It will miss things. It never
affects a verdict.

## 5. The check

### 5.1 Normalization

Applied identically to source text at load and to every claim quote at check
time:

- collapse all runs of whitespace to a single space
- straighten curly quotes and apostrophes to ASCII
- remove soft hyphens and join words broken across line breaks
- normalize unicode to NFKC
- strip leading and trailing whitespace

Nothing else. No case folding, no punctuation stripping, no stemming. Every
rule here must be reversible in the reader's head, because a user who cannot
predict the normalization cannot trust the verdict.

The normalized source is hashed at load. The hash appears in the report.

### 5.2 Reason codes

| Code             | Meaning                                                     |
| ---------------- | ----------------------------------------------------------- |
| `NOT_IN_SOURCE`  | Normalized quote does not appear in the normalized source   |
| `UNKNOWN_SOURCE` | Claim names a document that was never loaded                |
| `EMPTY_QUOTE`    | Quote is empty or whitespace only after normalization       |
| `BROKEN_LINEAGE` | `derived_from` points at a claim id that was never checked  |

A claim that passes gets no code. Every failure gets exactly one.

### 5.3 What is deliberately not checked

Whether the claim is true. Whether the quote supports the assertion built on
it. Whether the agent chose a relevant passage. Tattletale checks that the
words are in the document. That is a smaller promise than it sounds and it is
the only promise that can be kept deterministically.

## 6. Origin tracing

When a claim fails, Tattletale walks `derived_from` backward until it reaches
a claim with no parent. That claim's submitting agent is the origin.

```
summarizer submitted c_004, derived_from c_002
editor     submitted c_002, derived_from c_001
researcher submitted c_001, derived_from None    <- origin
```

Three cases the walk must handle:

1. **Parent not found.** Report the failure as `BROKEN_LINEAGE` and name the
   last known agent. Do not silently attribute to the submitter.
2. **Cycle.** Cap the walk at the number of recorded claims. On overrun, stop
   and report the chain as broken.
3. **Parent passed but child failed.** The child agent altered the quote.
   Origin is the child, not the parent. A modified quote is a new claim.

That last case is the one that earns the name. An agent that rewords a valid
quote into an invalid one gets caught and named, even though everything
upstream of it was clean.

## 7. Report format

The report is the product. It is what goes in the README and the terminal
recording.

```
TATTLETALE    8 claims     3 failed
source: contract.pdf       sha256:4f1a... (normalized)

summarizer          3 claims     2 FAILED
  c_004     "renews automatically every 24 months"
            NOT_IN_SOURCE
            inherited from: researcher (c_001)

  c_005     "indemnity capped at $2,000,000"
            NOT_IN_SOURCE
            originated here

researcher          5 claims     1 FAILED
  c_001    "renews automatically every 24 months"
           NOT_IN_SOURCE
           originated here

editor             0 claims      0 FAILED
```

Per-agent counts at the top of each block. Failed claims listed with quote,
reason, and origin. Agents with zero failures still appear, because a
summarizer that submitted zero claims is itself a finding.

JSON output carries the same content plus the source hash and every passing
claim.

## 8. Non-goals

Stated because each one is the road to a dead project.

- **No model calls.** Tattletale contains no LLM, no embeddings, no API key.
  It is arithmetic and string comparison.
- **No fuzzy matching.** A threshold turns every flagged claim into an
  argument about the threshold.
- **No mesh, bus, or orchestration.** It observes handoffs. It does not route
  them.
- **No framework integration in v1.** No LangGraph adapter, no CrewAI plugin.
  Those are v2 and only if people ask.
- **No truth claims.** It verifies quotation, not correctness. The README
  says so in the first paragraph.
- **No persistence.** A Monitor lives for one run. Export the JSON if you
  want history.

## 9. Build order

| Step | Deliverable                              | Proves                                                              |
| ---- | ---------------------------------------- | ------------------------------------------------------------------- |
| 1    | Normalizer plus tests                    | Messy input normalizes predictably and identically both sides       |
| 2    | `Monitor.check` with reason codes        | Fabricated quotes are rejected, with no lineage involved            |
| 3    | Lineage walk with the three edge cases   | Origin is named correctly, including reword-in-the-middle           |
| 4    | Text report                              | Output is legible to someone who has never seen the repo            |
| 5    | JSON report                              | Machine consumers have a stable shape                               |
| 6    | `extract.quoted_spans` helper            | Ten minute integration for people with unstructured messages        |
| 7    | Demo: 3-agent pipeline, planted fabrication | The GIF                                                          |
| 8    | Adversarial test suite                   | The claim survives contact with hostile input                       |

### Step 8 is the one that matters

Tests that feed it valid claims prove nothing. The suite that earns trust
attacks the checker: quotes with smart quotes against a straight-quote
source, quotes spanning a hyphenated line break, a claim citing a document
that was never loaded, a lineage cycle, a claim whose parent id was never
submitted, and an agent that subtly rewords a valid upstream quote. Each one
has an expected verdict and an expected named agent.

## 10. Demo

Three agents, one document, one planted fabrication.

`researcher` reads a short contract and returns four real quotes and one
invented clause. `editor` passes all five forward unchanged. `summarizer`
carries three of them, including the invented one, into a final summary.

The final output looks clean. Tattletale names `researcher`.

Under thirty seconds of terminal recording. That is the artifact.
