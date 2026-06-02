# 0001. Record architecture decisions

- Status: accepted
- Date: 2026-06-02
- Deciders: scaffold author
- Tags: process

## Context and problem statement

This project will accumulate architectural choices that are non-obvious from
the code alone: concurrency strategy, auth token lifecycle, caching policy,
migration rules. Without a durable record, future contributors (and the
evaluator of this take-home) cannot tell which decisions were deliberate and
which were accidental.

## Decision drivers

- Decisions must be discoverable from the repo, not from chat history.
- The cost of writing an ADR must be low enough that we actually write them.
- The format must survive being read months later.

## Considered options

- Free-form notes in `README.md` — low cost, but unstructured and lossy.
- Wiki / external doc tool — out of repo, drifts from code.
- MADR-style ADRs in `docs/adr/` — structured, version-controlled, reviewable.

## Decision outcome

Chosen option: **MADR-style ADRs in `docs/adr/`**, because they are versioned
with the code, keep a uniform shape, and are reviewable as part of the PR
that introduces the change.

### Positive consequences

- Every non-trivial decision has a single canonical home.
- Reviewers can read the ADR and the diff together.
- Superseded decisions stay in history with their successor linked.

### Negative consequences (the cost we accept)

- Small overhead per decision.
- Risk of "ADR sprawl" if used for trivial choices; mitigated by only writing
  ADRs for decisions that have at least one rejected alternative worth naming.

## When to write an ADR

- The decision has more than one credible option.
- The decision affects more than one module or persists beyond the current PR.
- Reversing the decision later would be expensive.

If none of these apply, a code comment or commit message is enough.

## Links

- [MADR](https://adr.github.io/madr/)
- [`docs/adr/template.md`](template.md)
