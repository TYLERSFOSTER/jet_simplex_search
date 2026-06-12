# Environment Construction For Benchmark Evaluations Protocol

## Status

Proposed prime-directive adjunct.

This document is directed to future Embedded Engineering Consultants working in
this repository.

Its purpose is to define what every benchmark environment must provide before
serious evaluations are designed on top of it.

## Core Rule

> An environment is not benchmark-ready until it exposes stable fixtures,
> contracts, diagnostics, artifacts, and human-readable context sufficient for
> evaluation construction.

Do not build an environment as only runnable code.

Do not let future evaluations infer environment intent from implementation
details alone.

Do not call an environment serious-ready until it can explain what is being
measured, what is legal, what reward means, what fixtures exist, what claims are
allowed, and how diagnostics prove the environment is sane enough to evaluate.

## Relationship To The Other Protocols

This is the first protocol in the benchmark workflow.

The evaluation construction protocol is:

```text
docs/prime_directive/evaluation_construction_for_readable_artifacts_protocol.md
```

The human-readout protocol is:

```text
docs/prime_directive/artifact_table_to_readable_document_protocol.md
```

The three stages are:

```text
1. Construct an environment that can support evaluations.
2. Construct evaluations for that environment.
3. Process run artifacts into repo-side human-readable readouts.
```

The environment protocol answers:

```text
What must the environment define before evaluations can be responsibly built?
```

## Required Environment Outputs

Every serious benchmark environment must define these outputs before evaluation
design begins.

### Environment Identity

Define stable ids for:

- environment family;
- environment instances or fixtures;
- smoke fixture;
- serious fixture;
- legality contract;
- reward bundle;
- action-mask policy;
- initial-state policy;
- terminal policy;
- edge/action label contract.

These ids must appear in docs and artifacts. They must not live only in code.

### Fixture Policy

Define fixture roles explicitly.

At minimum:

- smoke fixture: small enough for command/harness/artifact validation;
- serious fixture: large enough to support meaningful evaluation;
- any calibration fixture or scale tier;
- what each fixture may and may not claim.

Do not let a tiny/smoke fixture become serious evidence by accident.

### State, Action, And Transition Contract

Document:

- state representation;
- action representation;
- legal action mask semantics;
- transition semantics;
- terminal condition;
- invalid action behavior;
- whether dynamics are deterministic or stochastic;
- any hidden graph or latent structure;
- which fields are stable ids versus debug labels.

### Reward And Claim Contract

Document:

- reward bundle id;
- reward locality or path-dependence;
- whether reward uses future information;
- what a high or low return means;
- what reward cannot prove;
- whether reward is allowed to support domain-quality claims.

For musical or domain-rich environments, say explicitly whether reward is a
benchmark proxy or a domain-quality measure.

### Diagnostics

Every serious environment should provide diagnostics before serious evaluation.

Examples:

- graph size and edge counts;
- legality/mask coverage;
- path-volume diagnostics;
- reward-fiber diagnostics;
- schema/contraction diagnostics if tower methods apply;
- lift/action-realization diagnostics;
- timing and artifact-volume smoke checks.

Diagnostics must distinguish environment sanity from method performance.

### Structural Limit And Non-Claim Notes

If an environment exposes hidden graphs, quotient/tower methods, contraction
schemas, or lift/action-realization machinery, its environment docs must record
known structural limit cases before evaluation design begins.

At minimum, document:

- whether the runtime constructs the full hidden graph up front or discovers
  edges online;
- whether a contraction block acts as an edge-induced connected-component
  collapse;
- what it means if the first projection collapses `H` to `pi_0(H)` or nearly
  collapses all reachable concrete states into one quotient cell;
- which conclusions such a limit case can support;
- which conclusions such a limit case blocks;
- which diagnostics must be checked before describing behavior as performance,
  non-performance, mixed performance, or method failure.

For tower-control environments, do not leave this as an implicit fact of the
implementation. A full or near-full first-projection collapse can be a valid
environment/evaluation condition, but it must be presented as a structural
limit or pathology diagnostic unless the evaluation has explicitly been
designed to make a performance claim under that collapse.

The environment docs should tell later evaluation and readout work how to
separate:

- environment sanity;
- artifact completion;
- concrete action execution;
- quotient shape;
- lift/action-realization;
- learner performance;
- allowed claims and non-claims.

### Artifact Support

Environment runners must be able to write machine-readable artifacts through
the shared benchmark machinery.

At minimum, support:

- environment/family manifests;
- run manifests;
- dependency manifests;
- seed bundles;
- timing rows;
- metric rows;
- event rows;
- warnings;
- summaries;
- any environment-specific diagnostic tables.

If the environment interacts with `state_collapser` linearization or tower
machinery, write the linearization/backend condition into artifacts.

### Human Docs Seed

Every serious environment family should have a checked-in page under:

```text
docs/environments/
```

That page must include:

- what the environment is;
- why it exists;
- fixture ids and roles;
- legality/reward/action-mask contracts;
- diagnostics available;
- known structural limits or pathology cases;
- non-goals and claim boundaries;
- links to methods and evaluations that use it.

Environment docs may include readiness/status cues, but they must not use
evaluation-result badges unless those badges are backed by an executed
evaluation readout. Result badges belong to repo-side evaluation readout
surfaces under `docs/evaluations/`.

## Evaluation-Readiness Checklist

Before designing an evaluation for an environment, confirm:

- the environment has stable ids;
- smoke and serious fixtures are distinct;
- legality, reward, mask, initial-state, and terminal contracts are documented;
- diagnostics can be run and interpreted;
- known structural limits have written interpretation rules;
- artifacts are machine-readable and use shared machinery;
- human environment docs exist;
- non-goals and claim boundaries are explicit;
- intended evaluation arms can access the environment without hidden
  implementation assumptions.

## Required Tests

An environment implementation should include tests that fail if:

- fixture ids are unstable;
- smoke and serious fixtures are confused;
- legal action masks disagree with transitions;
- invalid action behavior is ambiguous;
- reward contracts are undocumented or inconsistent;
- diagnostics cannot be written as artifacts;
- environment docs omit fixture roles or claim boundaries;
- environment docs omit known structural limit cases for quotient/tower use;
- evaluation construction would need to infer environment intent from code only.

## Stop Conditions

Stop and ask the Project Owner before declaring an environment evaluation-ready
if:

- fixture roles are unclear;
- reward meaning is unclear;
- legality or action-mask semantics are unresolved;
- diagnostics are absent or uninterpretable;
- a known structural limit can change result interpretation but has no written
  claim boundary;
- artifact support is incomplete;
- the environment could support multiple incompatible evaluation meanings;
- claim boundaries are not known.

## Operating Summary

When building environments:

```text
Do not only make states and transitions.
Do not only make a runnable smoke.
Do not leave reward meaning implicit.
Do not let fixture roles blur.
Do not make evaluations infer environment contracts from code.

Define stable ids.
Define fixture roles.
Define legality, reward, mask, and terminal contracts.
Write diagnostics.
Write artifacts.
Write human environment docs.
Then build evaluations.
```
