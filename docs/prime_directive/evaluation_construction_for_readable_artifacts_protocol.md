# Evaluation Construction For Readable Artifacts Protocol

## Status

Proposed prime-directive adjunct.

This document is directed to future Embedded Engineering Consultants working in
this repository.

Its purpose is to define what every new benchmark evaluation must produce so
that `docs/prime_directive/artifact_table_to_readable_document_protocol.md` can
generate truthful, complete, human-readable readouts without reverse-engineering
the evaluation after the fact.

## Core Rule

> An evaluation is not construction-complete until it provides the machine
> evidence, source binding, goal context, methodology context, expected-file
> policy, and claim boundary needed by the human-readable readout protocol.

Do not treat human-readable docs as an afterthought.

Do not rely on a future consultant to infer evaluation intent from code alone.

Do not build an evaluation that can run but cannot explain what it was trying
to test, how it was tested, which files were expected, and which claims are
allowed.

## Relationship To The Other Protocols

This is the second protocol in the benchmark workflow.

The environment construction protocol is:

```text
docs/prime_directive/environment_construction_for_benchmark_evaluations_protocol.md
```

The downstream readout protocol is:

```text
docs/prime_directive/artifact_table_to_readable_document_protocol.md
```

The three stages are:

```text
1. Construct an environment that can support evaluations.
2. Construct evaluations for that environment.
3. Process run artifacts into repo-side human-readable readouts.
```

The construction protocol answers:

```text
What must an evaluation write or declare before a readout exists?
```

The readout protocol answers:

```text
How does Codex turn those artifacts and declarations into readable docs?
```

If a new evaluation does not satisfy this construction protocol, the readout
protocol will either produce weak prose, ask avoidable clarifying questions, or
misclassify absent files.

## Required Construction Outputs

Every evaluation must define these outputs before implementation is considered
complete.

### Repo Readout Surface

Define the repository folder where human-readable readouts live.

Example:

```text
docs/evaluations/counterpoint_symbolic_v001/first_serious_learning/
```

This folder owns the command target for the artifact-table readout protocol:

```text
execute docs/prime_directive/artifact_table_to_readable_document_protocol.md at <repo-readout-surface>/readout_source.json
```

The target is the checked-in `readout_source.json` file inside the repo readout
surface. It is not the README, the raw artifact root, or the raw evaluation
root.

### Source Artifact Shape

Define the artifact root and source evaluation root shape. For durable serious
evaluations, the artifact root must be repo-resident under the repo readout
surface:

```text
<repo-readout-surface>/artifacts/<run-label>/
```

At minimum, specify:

- artifact root argument or convention;
- evaluation id;
- source evaluation root path under the artifact root;
- run-family paths;
- result-table paths;
- per-run event paths.

If the evaluation uses `state_collapser` towers, active-tier control, quotient
schemas, or lift/action-realization, do not leave tower structure only in
per-run raw files. Promote the relevant evidence into evaluation-level result
tables that a human-readable readout can render directly.

At minimum, tower-control evaluations must provide:

- `results/tower_shape_summary.csv`: one row per arm/run/schema seed, including
  tier count and the state/action cell shape needed to interpret quotient
  collapse;
- `results/tier_occupancy_summary.csv`: active-tier dwell/controller counts
  by arm/run/schema seed/tier/action, including successful concrete steps by
  tier when available;
- `results/lift_failure_by_tier.csv`: lift/action-realization successes and
  failures by arm/run/schema seed/tier/reason.

Per-run raw files such as `quotient_summary.json`, `control_events.csv`,
`step_events.csv`, and `lift_fiber_events.csv` remain required evidence, but
they are not sufficient by themselves for a serious human-readable tower
evaluation. The evaluation-level tables are the surface that prevents future
readouts from needing to reverse-engineer tower shape and lower-tier time from
scratch.

### Source Binding

Every evaluation readout surface must include or be able to generate:

```text
readout_source.json
```

The source binding must include:

```json
{
  "repo_readout_surface": "<absolute repo path>",
  "source_artifact_root": "<raw artifact root>",
  "source_evaluation_root": "<raw evaluation root>",
  "evaluation_id": "<evaluation id>",
  "environment_instance_id": "<environment instance id>",
  "artifact_run_label": "<human run label>",
  "artifact_schema_version": "<artifact schema version>",
  "run_mode": "<run mode>",
  "source_files": {
    "aggregate_table": "<path to aggregate table>",
    "run_index": "<path to run index>"
  },
  "artifact_storage": {
    "mode": "git_tracked",
    "release_tag": null,
    "asset_name": null,
    "bundle_manifest_path": null
  },
  "expected_files": {
    "required": ["<required source file>"],
    "expected_absent_is_gap": [],
    "conditional": {},
    "not_applicable": [],
    "expectation_sources": ["<path documenting expectation policy>"]
  },
  "goal_criteria": [
    {
      "goal_id": "<stable goal id>",
      "question": "<question this goal answers>",
      "success_signal": "<artifact/table signal for success>",
      "partial_signal": "<artifact/table signal for partial or mixed result>",
      "failure_signal": "<artifact/table signal for failure>",
      "claim_if_met": "<claim supported if met>",
      "claim_if_not_met": "<claim blocked if not met>"
    }
  ],
  "badge_policy": {
    "dimensions": [
      "artifact_status",
      "behavioral_status",
      "goal_status",
      "claim_scope",
      "provenance_status"
    ]
  },
  "goal_summary_sources": ["<path documenting evaluation goals>"],
  "methodology_summary_sources": ["<path documenting evaluation methodology>"],
  "structural_limit_checks": [
    {
      "check_id": "<stable structural limit check id>",
      "trigger": "<artifact/table condition that triggers the check>",
      "interpretation_if_triggered": "<reader-facing interpretation>",
      "claim_effect": "<claim supported, blocked, or diagnostic-only>"
    }
  ],
  "claim_boundary": ["<allowed or excluded claim>"]
}
```

Do not omit `run_mode`. It is needed to distinguish calibration, smoke,
manually locked serious runs, calibration-derived serious runs, diagnostic
runs, and final result runs.

Do not omit `artifact_storage`. It tells public readout generation whether raw
artifacts are expected to remain in git or live in a GitHub release asset
bundle. If the storage mode is a release asset, include the release tag, asset
name, and bundle manifest path before regenerating public readouts.

Public-facing paths in source bindings and generated docs should be
repo-relative when possible. Machine-local absolute paths may appear only as
explicit local provenance fields, not as paths a public reader needs to run.

## Status Badge Inputs

Every evaluation must provide enough structured context for the readout
protocol to create a badge strip at the top of generated evaluation READMEs.

The default badge dimensions are:

| Dimension | Question |
| --- | --- |
| `artifact_status` | Did the expected machine-readable evidence exist? |
| `behavioral_status` | Did the evaluated system behavior succeed, fail, or mix? |
| `goal_status` | Were the evaluation goals met, partially met, blocked, or unknown? |
| `claim_scope` | What scope is the result allowed to claim? |
| `provenance_status` | Is the evidence durable, local, partial, or missing? |

Evaluation construction should not hard-code the final badge colors unless the
status is known before execution. It should define the evidence and goal
criteria needed to derive them.

At minimum, include `goal_criteria` in `readout_source.json` or in a source doc
referenced by `goal_summary_sources`.

Use stable goal ids. Each goal should say:

- the question being tested;
- the artifact/table fields that indicate success;
- the artifact/table fields that indicate partial or mixed behavior;
- the artifact/table fields that indicate failure;
- the claim supported if the goal is met;
- the claim blocked if the goal is not met.

The readout protocol may derive badges from artifacts, `expected_files`,
`goal_criteria`, `claim_boundary`, `run_mode`, and provenance paths. It must not
invent a green badge from prose optimism.

After readout generation, `readout_source.json` may also contain
`readout_badges`. Treat that as cached derived readout state. It is useful for
regeneration, but it is not a substitute for `goal_criteria` or artifact
evidence.

If an evaluation writes or caches badge inputs, keep badge `label` and `value`
as separate fields. The `value` should be reader-facing text such as
`Complete`, `Limited Signal`, `Negative Signal`, or `Repo Artifacts`, not a raw
`snake_case` enum copied directly from an aggregate table. Raw machine statuses
remain available in result tables; badge text is a visual summary layer for
humans.

## Structural Limit Checks

Every quotient-schema, tower-control, hidden-graph contraction, or
lift/action-realization evaluation must declare structural limit checks before
the readout exists.

The evaluation must say how the readout should interpret cases where the
runtime is valid but the quotient structure changes the meaning of the result.
This is especially important when a contraction block can behave like:

```text
H -> pi_0(H)
```

under the first projection.

At minimum, tower-control evaluations must define checks for:

- full first-projection collapse, for example tier `1` has one state cell;
- near-full first-projection collapse, for example the largest tier-`1` fiber
  contains at least 90 percent of tier-`0` states;
- universal or overly broad first contraction blocks;
- zero-step or low-step tower episodes caused by lift/action-realization
  failures;
- cases where artifact completion succeeds but performance claims are blocked.

These checks must identify the source tables or per-run files that support the
classification. For the current counterpoint tower work, the relevant sources
include:

- `results/tower_shape_summary.csv`;
- `results/tier_occupancy_summary.csv`;
- `results/lift_failure_by_tier.csv`;
- `results/schema_diagnostic_summary.csv`;
- per-run `quotient_summary.json`, `control_events.csv`, `step_events.csv`, and
  `lift_fiber_events.csv` when evaluation-level summaries are not sufficient.

Do not let `mixed` become the default label for a structural limit case. A run
may be behaviorally mixed in the narrow table sense while still requiring a
reader-facing classification such as diagnostic-only, structural-limit case,
claim-blocking quotient collapse, or lift-realization failure. The construction
contract must give the readout protocol enough context to choose that language
without guessing.

## Expected-File Policy

Every evaluation must declare expected files by expectation class.

Use this shape:

```json
{
  "expected_files": {
    "required": [],
    "expected_absent_is_gap": [],
    "conditional": {},
    "not_applicable": [],
    "expectation_sources": []
  }
}
```

Meanings:

| Field | Meaning |
| --- | --- |
| `required` | Must exist for this source artifact set to be interpretable. |
| `expected_absent_is_gap` | Expected by the evaluation contract; absence is a provenance or artifact gap. |
| `conditional` | Expected only for named run modes or conditions. |
| `not_applicable` | Explicitly not applicable for this run mode or claim boundary. |
| `expectation_sources` | Docs or source files that justify this policy. |

Do not let the readout protocol guess whether absent files are missing,
conditional, or not applicable.

## Goal Summary Material

Every evaluation must provide enough material for the README section:

```markdown
## Summary of Goals Behind this Evaluation
```

The construction artifacts must answer:

- what question the evaluation exists to answer;
- why this environment or fixture was chosen;
- what arms, baselines, controls, and comparison groups matter;
- what success or failure would mean;
- what non-goals and claim exclusions apply.

Record the source material in:

```json
{
  "goal_summary_sources": [
    "docs/design/<evaluation-blueprint>.md",
    "docs/evaluations/<evaluation>/method.md",
    "readout_source.json"
  ]
}
```

## Methodology Summary Material

Every evaluation must provide enough material for the README section:

```markdown
## Summary of Methodology Behind this Evaluation
```

The construction artifacts must answer:

- evaluation method class and comparison design;
- environment fixture and why that fixture is the serious or smoke target;
- arms, baselines, controls, and what each arm tests;
- budget, seeds, schema seeds, episode horizon, and replicates;
- calibration, run, summarize, and readout path distinction;
- artifact contract and expected-file policy;
- aggregation/statistics method;
- timing categories and what timing cannot claim;
- linearization/backend condition;
- claim boundary and non-goals.

Record the source material in:

```json
{
  "methodology_summary_sources": [
    "docs/design/<evaluation-blueprint>.md",
    "docs/evaluations/<evaluation>/method.md",
    "docs/evaluations/<evaluation>/runbook.md",
    "readout_source.json"
  ]
}
```

If methodology differs by run mode, the source binding must say so. For
example, calibration methodology and locked serious-run methodology are not the
same thing.

## Evaluation Manifests

Every serious evaluation should write evaluation-level manifests unless the
Project Owner explicitly approves a narrower run mode.

At minimum:

```text
evaluation_manifest.json
evaluation_arm_manifest.json
evaluation_run_index.csv
evaluation_budget_lock.json
evaluation_aggregate_summary.json
evaluation_aggregate_table.csv
```

Tower-control or quotient-schema evaluations should additionally write:

```text
results/tower_shape_summary.csv
results/tier_occupancy_summary.csv
results/lift_failure_by_tier.csv
```

These are not optional niceties for active-tier evaluations. They are the
machine-readable bridge between raw tower artifacts and human-readable
interpretation.

Calibration paths should additionally write:

```text
calibration_summary.json
calibration_run_index.csv
calibration_recommendation.md
```

If a run mode does not write a file from the broader contract, record that in
`expected_files` as `conditional` or `not_applicable`, not as an implicit
absence left for the readout to guess.

## Human Docs Seeds

Every evaluation should have checked-in human-doc seed files under its repo
readout surface:

```text
README.md
method.md
runbook.md
artifact_index.md
results/summary.md
```

These files do not replace machine-readable artifacts. They provide stable
context for goal and methodology summaries and make readouts auditable by a
human.

## Required Tests

An evaluation implementation should include tests that fail if:

- `readout_source.json` cannot be generated or parsed;
- required source files are not listed;
- expected-file policy is absent;
- `goal_summary_sources` is empty;
- `methodology_summary_sources` is empty;
- the repo readout surface is confused with the raw artifact root;
- README generation would leave `[...]`, `TODO`, or `TBD`;
- calibration-only files are treated as required for every run mode;
- serious evaluation manifests are omitted without explicit policy.
- tower-control evaluations omit tower shape, tier occupancy, or lift failure
  summary tables while still expecting human-readable interpretation.

## Stop Conditions

Stop and ask the Project Owner before implementing or declaring an evaluation
complete if:

- the evaluation goal is not clear enough to populate the README goal summary;
- the methodology is not clear enough to populate the README methodology
  summary;
- expected files cannot be classified;
- run modes are not distinguished;
- source paths are ambiguous;
- claim boundaries are not known;
- a generated readout would need to infer intent from code only.

## Operating Summary

When building evaluations:

```text
Do not only make the run executable.
Do not only make tables.
Do not leave readout intent implicit.
Do not make future readouts guess expected files.
Do not leave goal or methodology summaries as placeholders.

Build the evidence.
Bind the evidence to a repo readout surface.
Declare file expectations.
Declare goal sources.
Declare methodology sources.
Declare claim boundaries.
Then the readout protocol can translate rather than reconstruct.
```
