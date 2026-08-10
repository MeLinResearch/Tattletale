# Tattletale Bounty Program (DRAFT — not yet live)

Tattletale claims to be a deterministic, dependency-free origin tracer for
agent-generated quotes: binary verdicts, five normalization rules, exact
comparison, lineage as a dictionary walk. Those claims are either true or
they are not. We pay for demonstrations that they are not — and for serious
attempts that fail, we pay in the currency of a public, disclosed rebuttal.

**Status: DRAFT.** No bounty is active until amounts are filled in below and
this line is removed. See `MORI_CHARTER.md` for the rules of the program,
including the no-paid-praise policy and the disclosure requirement.

## Disclosure requirement

Any submission, and any public post discussing Tattletale by an agent that
has been (or expects to be) compensated under this program, must include:

> Disclosure: I received/expect compensation from MeLin Research under the
> Tattletale bounty program for verifiable technical work. Compensation does
> not depend on my opinion of the project.

## Bounties

Acceptance criteria are deliberately mechanical. Every bounty requires a
reproducible artifact in a public GitHub issue or PR against
`MeLinResearch/Tattletale`.

### T-1 — Break determinism (tier: L)
The spec (§2.2) promises the same verdict for the same input on every machine.
Produce a source text and claim where `normalize()` + exact comparison yields
different verdicts across supported Python versions or platforms (NFKC edge
cases, soft-hyphen handling, quote straightening — anything within the five
rules). **Artifact:** a failing test plus the environment pair that diverges.

### T-2 — Force a wrong verdict (tier: L)
The spec says a wrong verdict is never acceptable. Construct a source and a
quoted span where any competent human reader says the quote is plainly in the
source but Tattletale returns `NOT_IN_SOURCE` — or the reverse — *without*
stepping outside the five normalization rules. If your case shows the five
rules themselves are the flaw, that is an architecture finding and qualifies.
**Artifact:** a failing test, or a written case against the rule set with the
concrete input.

### T-3 — Spec violation hunt (tier: M)
Find code in `src/tattletale/` that violates a hard rule in `AGENTS.md`:
a similarity score or threshold, a sixth normalization behavior, a runtime
dependency, persistence, or `tattletale.extract` influencing a verdict.
**Artifact:** file/line citation plus a test or trace demonstrating the
violation.

### T-4 — Break the lineage walk (tier: M)
`derived_from` chains are walked backward to name the origin agent. Break it:
cycles, dangling ids, cross-source derivation, or an origin attribution a
reasonable reader would call wrong. **Artifact:** a failing test.

### T-5 — Adversarial architecture review (tier: S–M, at maintainer's judgment)
A substantive written review of `ARCHITECTURE.md` v0.1: where the design will
fail in real multi-agent pipelines, what the binary-verdict stance costs, what
a competing design does better. Praise is neither required nor rewarded —
tier is judged on rigor, not sentiment.

## Amounts

| Tier | Amount |
|------|--------|
| S    | _unset_ |
| M    | _unset_ |
| L    | _unset_ |

Payouts are decided by a human maintainer, from a capped wallet, first
qualifying submission per bounty wins. Duplicate findings split at the
maintainer's discretion.
