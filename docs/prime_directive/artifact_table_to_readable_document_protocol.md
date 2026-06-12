# Artifact Tables To Readable Documents Protocol

## Status

Proposed prime-directive adjunct.

This document is directed to future Embedded Engineering Consultants working in
this repository.

Its purpose is to define how machine-readable benchmark artifacts, especially
tables, should be translated into human-readable documents without losing
evidence, hiding failures, or inventing claims.

## Problem

Benchmark systems naturally produce files that are readable to engineers:

- JSON manifests;
- CSV aggregate tables;
- CSV event rows;
- timing summaries;
- run indices;
- diagnostic rows;
- artifact indexes.

Those files are necessary. They are not sufficient.

A human reader who does not already know the benchmark internals should not have
to infer the story from:

- raw arm ids;
- path-heavy artifact indexes;
- nested run directories;
- status fields that mean "artifact complete" rather than "behavior successful";
- diagnostic details buried several files away from the summary;
- local abbreviations such as `lift`, `fiber`, `schema`, `tier`, or `mode`.

The core failure mode is:

```text
machine evidence exists, but the human-facing document does not translate it
into a truthful, readable explanation.
```

## Core Rule

> A result document must tell the reader what happened, how we know, what it
> means, what it does not mean, and where the machine evidence lives.

Do not treat a table copy, artifact index, or manifest list as a human result
report.

Do not summarize away the evidence.

The readable document must preserve the path back to the artifacts while
explaining the artifacts in ordinary engineering language.

## Relationship To The Other Protocols

This is the third protocol in the benchmark workflow.

The environment construction protocol is:

```text
docs/prime_directive/environment_construction_for_benchmark_evaluations_protocol.md
```

The evaluation construction protocol is:

```text
docs/prime_directive/evaluation_construction_for_readable_artifacts_protocol.md
```

The three stages are:

```text
1. Construct an environment that can support evaluations.
2. Construct evaluations for that environment.
3. Process run artifacts into repo-side human-readable readouts.
```

This readout protocol answers:

```text
How does Codex turn artifacts and source bindings into readable docs?
```

## Non-Negotiable Path Invariants

The protocol has three different path roles. Do not merge them.

```text
repo_readout_surface:
  The folder named by the Project Owner in the invocation.
  The human-readable files are written here.
  This folder is inside this repository.

source_artifact_root:
  The raw benchmark artifact root.
  For generated evaluation readouts, this must be inside the repository under
  the repo readout surface, usually
  <repo_readout_surface>/artifacts/<run-label>/.
  This is evidence metadata, not the invocation target.

source_evaluation_root:
  The evaluation subfolder containing aggregate tables and result tables.
  This is evidence metadata, not the invocation target.
```

The invocation folder always means `repo_readout_surface`.

If the Project Owner accidentally points the command at `source_artifact_root`
or `source_evaluation_root`, stop and ask for the repo-side readout surface.
Do not write generated readouts into the artifact tree.

## Consultant Invocation Surface

This protocol defines a you-readable surface: a natural-language command the
Project Owner can give to an Embedded Engineering Consultant without needing a
separate shell script.

The canonical invocation is:

```text
execute docs/prime_directive/artifact_table_to_readable_document_protocol.md at <repo-readout-surface>/readout_source.json
```

Equivalent accepted invocations:

```text
execute artifact-table-to-readable-document protocol at <repo-readout-surface>/readout_source.json
apply docs/prime_directive/artifact_table_to_readable_document_protocol.md to <repo-readout-surface>/readout_source.json
generate the human readout from <repo-readout-surface>/readout_source.json using docs/prime_directive/artifact_table_to_readable_document_protocol.md
```

When the Project Owner gives one of these commands, the consultant must treat it
as an instruction to:

1. read this protocol;
2. resolve the supplied file as a repository-side `readout_source.json` source
   binding;
3. read that source binding to find the repo readout surface and the
   machine-readable artifacts;
4. write the human-readable files required by this protocol;
5. report exactly what was written and what could not be interpreted.

The Project Owner should not need to restate the document shape, claim-boundary
rules, all-cases protocol, or evidence discipline. Those are supplied by this
protocol.

### Reminder Rule

When the conversation touches any of the following:

- evaluation artifacts;
- unreadable result tables;
- aggregate CSVs;
- result docs;
- benchmark evidence;
- "what happened in this run?";
- "how do I read this?";
- "make this human-readable";
- confusion about `complete` versus successful behavior;
- confusion about zero, null, missing, or failed metrics;

the consultant should remind the Project Owner of the invocation surface:

```text
execute docs/prime_directive/artifact_table_to_readable_document_protocol.md at <repo-readout-surface>/readout_source.json
```

The reminder should be short and optional, not a derailment.

Good reminder:

```text
For this repo, the protocol surface is:
execute docs/prime_directive/artifact_table_to_readable_document_protocol.md at <repo-readout-surface>/readout_source.json
```

Here `<repo-readout-surface>/readout_source.json` is the checked-in source
binding, usually somewhere under `docs/evaluations/`. It is not the README, the
raw artifact directory, or the raw evaluation directory.

Bad reminder:

```text
Here is a new multi-step workflow you should follow...
```

Do not repeatedly remind the Project Owner inside the same local conversation
unless the Project Owner appears to be searching for the command again.

### Source Binding Resolution

The invocation must include an explicit repository `readout_source.json` file.
Relative paths are resolved from the repository root. Do not infer "last run"
unless the Project Owner explicitly adds a reliable source binding.

The supplied `<file>` is the source binding. It is not the README, the raw
artifact root, and it is not the raw evaluation root. The repo-side readout
surface is read from the `repo_readout_surface` field in that source binding.

For this repository's first serious counterpoint evaluation, the normal command
target is:

```text
execute docs/prime_directive/artifact_table_to_readable_document_protocol.md at docs/evaluations/counterpoint_symbolic_v001/first_serious_learning/readout_source.json
```

Resolve the supplied source binding as follows:

1. If the file is outside the repository, stop. Tell the Project Owner that the
   protocol must be pointed at a checked-in repo-side `readout_source.json`.
2. If the file is not named `readout_source.json`, stop and ask for the source
   binding unless the Project Owner explicitly says the file is a compatible
   source binding.
3. If the file does not exist, stop and ask for the correct source binding. Do
   not create a source binding from memory unless the Project Owner explicitly
   asks for source-binding construction.
4. Read `repo_readout_surface`, `source_artifact_root`,
   `source_evaluation_root`, and `source_files` from `readout_source.json`.
5. If `repo_readout_surface` is outside the repository, stop.
6. If `source_artifact_root` is outside the repository for a durable evaluation
   readout, stop and ask whether to rerun or copy source tables into a
   repo-resident artifact root.
7. If required source files listed in `readout_source.json` are missing, apply
   the expected-file classification rules. Do not silently reuse older tables.
8. If the Project Owner uses the old folder-based command, treat it as
   ambiguous. Ask them to run the explicit command against that folder's
   `readout_source.json`.

### Public Release Hygiene Mode

When generating or regenerating readouts for a public beta/release branch,
apply these extra constraints:

- use repo-relative paths or explicit placeholders such as `<repo-root>`;
- do not write machine-local absolute paths into public Markdown;
- if a manifest preserves local provenance, label the field as local
  provenance and do not make it part of the public command path;
- use `[XXX]` for public profanity redaction while preserving attribution and
  meaning;
- do not invent Project Owner turns or convert consultant-authored text into
  Project Owner text;
- do not use ambiguous "last run" or folder-only source inference;
- write or preserve `artifact_storage` metadata when raw artifacts are stored
  in release assets instead of git;
- keep badge labels visually consistent with other public readouts;
- do not leave unexplained empty placeholder turn pads in public readout
  READMEs.

If these constraints conflict with a historical open-lab archive, preserve the
archive's attribution and add a neutral public-release note rather than
silently rewriting history.

### Source Binding

Every repo readout surface should have a source binding file:

```text
<repo-readout-surface>/readout_source.json
```

It should record at least:

```json
{
  "repo_readout_surface": "<absolute repo path>",
  "source_artifact_root": "<raw artifact root>",
  "source_evaluation_root": "<raw evaluation root>",
  "evaluation_id": "<evaluation id>",
  "artifact_run_label": "<human run label>",
  "source_files": {
    "aggregate_table": "<path to evaluation_aggregate_table.csv>",
    "run_index": "<path to evaluation_run_index.csv>",
    "learning_curves": "<path to results/learning_curves.csv>"
  },
  "artifact_storage": {
    "mode": "git_tracked_or_github_release_asset",
    "release_tag": "<release tag when externalized>",
    "asset_name": "<release asset name when externalized>",
    "bundle_manifest_path": "<bundle manifest path when externalized>"
  }
}
```

When possible, `readout_source.json` should also record expected-file policy so
the human readout can distinguish real missing evidence from files that are not
applicable to this run mode:

```json
{
  "expected_files": {
    "required": ["evaluation_budget_lock.json", "evaluation_run_index.csv"],
    "expected_absent_is_gap": [
      "evaluation_manifest.json",
      "evaluation_arm_manifest.json"
    ],
    "conditional": {
      "calibration": [
        "calibration_summary.json",
        "calibration_run_index.csv",
        "calibration_recommendation.md"
      ]
    },
    "not_applicable": []
  }
}
```

When possible, `readout_source.json` should also record the goal-summary source
for the README:

```json
{
  "goal_summary_sources": [
    "docs/design/<evaluation-blueprint>.md",
    "docs/evaluations/<evaluation>/method.md",
    "readout_source.json"
  ]
}
```

This is not a substitute for the README goal summary. It is an audit pointer
showing where the generated prose came from.

When possible, `readout_source.json` should also record the methodology-summary
source for the README:

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

This is not a substitute for the README methodology summary. It is an audit
pointer showing where the generated prose came from.

If the source binding lacks expected-file policy, do not flatten all absent
files into "missing evidence." Use the evaluation design docs, artifact
contract, run mode, and available manifests to classify each absent file as:

```text
present
expected_missing_gap
conditional_absent
not_applicable
unknown_expectation
```

The source artifact root for an evaluation readout must live inside the repo
readout surface under `artifacts/<run-label>/`. Do not bind a generated
evaluation report to an outside-repo scratch location; rerun or copy the source
tables into the repo-resident artifact root first.

### Output Location

Write the readable documents into the supplied repo readout surface.

For example:

```text
<repo-root>/docs/evaluations/counterpoint_symbolic_v001/first_serious_learning
```

Do not write under `docs/results/` unless the Project Owner explicitly asks to
promote a final result summary there.

Do not write human-readable readouts under an outside-repo scratch location, an
artifact root, or a raw evaluation root.

### Execution Contract

The consultant must first resolve the source binding, then inspect, when
present:

- `evaluation_manifest.json`;
- `evaluation_arm_manifest.json`;
- `evaluation_budget_lock.json`;
- `evaluation_run_index.csv` or `calibration_run_index.csv`;
- `calibration_summary.json`;
- `evaluation_aggregate_summary.json`;
- `evaluation_aggregate_table.csv`;
- `results/learning_curves.csv`;
- `results/timing_summary.csv`;
- `results/controller_summary.csv`;
- `results/schema_diagnostic_summary.csv`;
- `results/tower_shape_summary.csv`, when the evaluation uses towers or
  quotient schemas;
- `results/tier_occupancy_summary.csv`, when the evaluation uses active-tier
  control;
- `results/lift_failure_by_tier.csv`, when the evaluation performs
  lift/action-realization;
- representative per-run `episodes.csv`;
- representative per-run `quotient_summary.json`, when present;
- representative per-run `control_events.csv`;
- representative per-run `step_events.csv`;
- representative per-run `lift_fiber_events.csv`;
- representative per-run `warnings.jsonl`;
- representative per-run manifests needed to interpret claim boundaries.

If the artifact set is large, inspect representative per-run files for every
arm class and every anomalous condition before writing the final readout.

For tower-control evaluations, do not stop at arm-level means. The readout must
translate tower shape and active-tier occupancy into human language. If
evaluation-level tower tables exist, use them. If they are absent but per-run
raw files exist, reconstruct the minimum supported shape/occupancy story from
`quotient_summary.json`, `control_events.csv`, `step_events.csv`, and
`lift_fiber_events.csv`, then classify the missing evaluation-level tables as
an artifact/readout gap. Do not make a reader infer lower-tier behavior from
raw ids alone.

If a required source file listed in `readout_source.json` is absent, do not
silently reuse an older table. Classify it as `expected_missing_gap` and apply
the relevant all-cases rule.

If a source file is absent but not listed as required, classify expectation
before writing the report. For example, calibration files may be absent because
the source artifact root came from a manually locked serious run rather than a
calibration path. In that case, call them `conditional_absent` or
`not_applicable`; do not call them missing evidence unless the source binding,
blueprint, or run mode says they were expected for this artifact set.

### Output Contract

The default output set is:

```text
<repo-readout-surface>/
  readout_source.json
  README.md
  result_readout.md
  runbook.md
  artifact_index.md
  glossary.md
  badges/
    artifacts_<status>.svg
    behavior_<status>.svg
    goals_<status>.svg
    scope_<status>.svg
    provenance_<status>.svg
  results/
    summary.md
    human_summary.md
    arm_readout_table.md
    diagnostic_findings.md
    timing_readout.md
```

If the existing repo-local readout already contains some of these files, update
or replace them only as needed to satisfy this protocol. Preserve useful
existing runbook or artifact-index information.

If a prior version of this protocol wrote artifact-local docs under
`<evaluation-root>/docs/`, treat those files as non-authoritative temporary
readouts unless the Project Owner explicitly asks to preserve or migrate them.

### README Badge Surface

Every generated evaluation `README.md` must include a visual badge strip near
the top of the file, immediately after the title and before the long prose
summary.

The default badge dimensions are:

| Badge | Meaning |
| --- | --- |
| `Artifacts` | Whether expected machine-readable evidence exists. |
| `Behavior` | Whether evaluated behavior succeeded, failed, mixed, or was not tested. |
| `Goals` | Whether evaluation goals were met, partially met, blocked, or unknown. |
| `Scope` | The strongest allowed claim scope, such as smoke, fixture-only, or promoted result. |
| `Provenance` | Whether evidence is durable, local, partial, or missing. |

Do not create one global pass/fail badge. Artifact completion, behavioral
success, goal satisfaction, claim scope, and provenance are different facts.

Badges must be local generated SVG files under:

```text
<repo-readout-surface>/badges/
```

Do not use remote badge services. A readout must remain inspectable offline and
must not depend on network access.

### Badge SVG Shape And Text Contract

Generated badge SVGs must follow the established local shield format used by
the existing evaluation readouts:

```text
left segment:  reader-facing label, dark gray background
right segment: reader-facing value, status-color background
height:        20px
markdown:      ![<Label>: <Value>](badges/<badge_id>.svg)
```

The left label and right value are separate fields. Do not create a one-piece
badge whose single text string is `Label: value`.

Use this SVG structure unless a repository-wide badge helper supersedes it:

```text
<rect width="<label-width>" height="20" fill="#555"/>
<rect x="<label-width>" width="<value-width>" height="20" fill="<status-color>"/>
<text ... text-anchor="middle">Label</text>
<text ... text-anchor="middle">Value</text>
```

Use the same visual family as the existing counterpoint reports:

```text
green:  #2e7d32
yellow: #b58900
orange: #ef6c00
red:    #d32f2f
blue:   #1565c0
label:  #555
```

Badge text is reader-facing text, not raw machine status. Translate
`complete_limited_signal` to a value such as `Limited Signal`,
`paired_comparison_negative_signal` to `Negative Signal`, and
`threshold_calibrated` to `Calibrated`. Raw `snake_case` ids may appear in
tables and provenance fields, but they must not appear as badge text unless the
raw id itself is the object being reported.

Before writing a new badge set, remove stale generated SVGs from
`<repo-readout-surface>/badges/`. A badge folder must not keep obsolete badge
files from a prior run mode.

Use this color policy:

| Color | Meaning |
| --- | --- |
| green | Satisfied, complete, passed, or supports the bounded claim. |
| yellow | Partial, mixed, warning, or limited. |
| orange | Gap, degraded evidence, local-only provenance, or interpretation risk. |
| red | Failed, missing required evidence, or claim unsupported. |
| gray | Not applicable, not evaluated, or unknown. |
| blue | Informational scope badge. |

Each badge label must be derivable from artifacts and source binding context:

- `readout_source.json`;
- `expected_files`;
- `goal_criteria`;
- aggregate/result tables;
- run index;
- diagnostics;
- claim boundary;
- run mode and provenance paths.

If `readout_source.json` contains `readout_badges`, treat those entries as
cached derived readout state, not as evidence. Verify them against the current
artifact tables and update stale labels, colors, file paths, and reasons.
`readout_badges` entries must preserve separate `label` and `value` fields so
the README can render `![Label: Value](...)` without recombining internal enum
strings.

If a badge cannot be derived, use an `Unknown` gray badge and mirror the missing
context into `Clarifying Questions And Turns`.

Every generated evaluation `README.md` must also include a short
`Status At A Glance` section immediately after the badge strip. Use bullets.
The bullets must explain the badge labels in ordinary engineering language.
This section is intentionally compact; detailed evidence belongs in the main
readout and result files.

### README Turn Surface

Every generated `README.md` must end with a place for human/consultant turns.
This is part of the readout surface, not a separate design document.

On first generation, create this exact section at the bottom of `README.md`
unless the Project Owner gives different labels:

```markdown
## Clarifying Questions And Turns

#### Project Owner / Evaluator Turn

> ...

#### Embedded Engineering Consultant / Codex Turn

> ...

#### Project Owner / Evaluator Turn

> ...

#### Embedded Engineering Consultant / Codex Turn

> ...

#### Project Owner / Evaluator Turn

> ...

#### Embedded Engineering Consultant / Codex Turn

> ...
```

Use this section for:

- unresolved source-binding questions;
- unclear claim boundaries;
- ambiguous zero/null/failure interpretation;
- missing baseline decisions;
- PO/evaluator corrections to the readout;
- Codex replies that explain how the report was changed or why a claim was
  blocked.

Do not use this section to narrate normal findings that already belong in the
verdict, result table, diagnostics, or evidence map.

Do not put words in the Project Owner's mouth. The placeholder `> ...` means
"available for a future turn"; it is not content and must not be interpreted as
an answer.

### README Turn Preservation

On subsequent generations, treat `## Clarifying Questions And Turns` as
protected conversation state.

Do not:

- delete it;
- reorder it;
- rewrite existing turns;
- summarize existing turns;
- replace existing turns with generated text;
- move it away from the bottom of `README.md`;
- convert `####` turn headings back to `###`;
- replace `> ...` placeholders with prose.

Regeneration may update sections above `## Clarifying Questions And Turns`.
The turn section itself must remain byte-for-byte intact whenever it already
contains at least one Project Owner / Evaluator and Embedded Engineering
Consultant / Codex turn pair.

If the section is missing, generate the initial three blank turn pairs shown
above.

For public release READMEs, do not leave the blank turn pairs visually
ambiguous. If no actual clarification turns exist, either omit the turn pad or
write a compact note such as:

```markdown
## Clarifying Questions And Turns

_No active public clarification turns are recorded for this readout._
```

If actual turns exist, preserve them under their true attribution headings and
append new empty slots only when the Project Owner explicitly asks to continue
conversation in that readout.

If the section exists but contains no complete Project Owner / Evaluator plus
Embedded Engineering Consultant / Codex turn pair, append the initial three
blank turn pairs inside the existing section, preserving any existing text.

If the section exists and all blank `> ...` turn pairs have been filled, append
one new blank Project Owner / Evaluator plus Embedded Engineering Consultant /
Codex turn pair at the end, preserving all previous turns.

### Completion Report

After executing this surface, report:

- the input folder, meaning the repo readout surface;
- the resolved source artifact root;
- the resolved source evaluation root;
- the files written;
- any absent artifacts, classified by expectation status;
- any stopped claim decisions;
- validation performed, if any.

Do not merely say "done" if the readout contains warnings or blocked claims.

## Translation Ladder

Every table-to-document translation must move through this ladder:

1. Artifact location
2. Artifact type
3. Field meaning
4. Observed values
5. Interpretation
6. Claim boundary
7. Inspection path

Example:

```text
evaluation_aggregate_table.csv
-> aggregate arm table
-> mean_return is average episode total reward
-> non-empty tower arms have mean_return 0.0 and step_count 0
-> these arms completed as artifact runs but failed behaviorally
-> this does not support a tower-performance claim
-> inspect lift_fiber_events.csv and control_events.csv for failure mechanism
```

Skipping steps creates misleading documents.

## Required Reader Layers

A readable benchmark report should serve three reader layers.

### 1. First-Contact Reader

This reader wants to know:

- what was run;
- whether it worked;
- what the big result was;
- whether any result is surprising or invalidating;
- whether the report is making a benchmark claim.

This reader should not need to understand file layout or internal ids.

### 2. Technical Reviewer

This reader wants:

- arm ids;
- exact budgets;
- seeds and schema seeds;
- baselines;
- confidence intervals;
- timing categories;
- diagnostic failure rates;
- artifact paths.

This reader should be able to audit the result without guessing which file
matters.

### 3. Future Engineer

This reader wants:

- what to rerun;
- which files to inspect first;
- what anomalies are already known;
- what implementation behavior may need fixing;
- which claims are allowed or blocked.

This reader should be able to resume work without rediscovering the same
interpretation from scratch.

## Required Document Shape

When generating or writing a human-facing result document from artifact tables,
use this shape unless the Project Owner asks for a different one.

### 1. Title

Name the evaluation, environment, and run class.

Bad:

```text
Results Summary
```

Better:

```text
Counterpoint First Serious Learning Evaluation - Human Readout
```

### 2. Badge Strip And Status At A Glance

Every generated evaluation `README.md` must place local SVG badges immediately
under the title.

Example:

```markdown
![Artifacts: Partial](badges/artifacts_partial.svg)
![Behavior: Mixed](badges/behavior_mixed.svg)
![Goals: Partial](badges/goals_partial.svg)
![Scope: Fixture Only](badges/scope_fixture_only.svg)
![Provenance: Repo Artifacts](badges/provenance_repo_artifacts.svg)
```

These Markdown links are examples of the required `Label: Value` alt-text
contract. The SVGs behind them must be the two-segment local shield style
defined above. Do not emit raw internal values such as
`![Suite: complete_limited_signal](...)` or one-piece long badges.

Then include:

```markdown
## Status At A Glance

- Artifact evidence: partial; required result tables exist, but expected
  provenance manifests are absent.
- Behavioral result: mixed; direct arms and the empty-schema tower execute real
  steps, while non-empty tower arms expose lift/action-realization failures.
- Goal result: partially met; the run validates the serious harness and exposes
  a tower-control failure mechanism, but does not show tower advantage.
- Claim scope: fixture-only; claims apply only to the named environment,
  budget, seeds, and linearization condition.
- Provenance: repo-resident artifact root; evidence is source-bound from this
  repo readout surface.
```

The badge strip and status bullets must agree with the detailed verdict,
provenance status, and claim boundary. If they disagree, fix the readout before
returning it.

The example `Behavior: Mixed` badge is not a default. Use it only when mixed
behavior is the correct reader-facing classification after structural
diagnostics have been checked. For quotient-schema or tower-control
evaluations, first check whether the apparent mixed behavior is dominated by a
structural limit case such as:

- the first projection collapses all tier-`0` states into one tier-`1` cell;
- the first projection nearly collapses all tier-`0` states, for example the
  largest tier-`1` fiber contains at least 90 percent of tier-`0` states;
- the first contraction block is universal or broad enough to act like an
  edge-induced connected-component collapse;
- concrete action execution is blocked by lift/action-realization at the
  collapsed tier.

If one of these conditions explains the result, the status line must say so in
the headline status area. Prefer a reader-facing status such as
`Behavior: Diagnostic`, `Behavior: Structural Limit`, or `Goals: Blocked` over
plain `Behavior: Mixed`. If the local badge vocabulary has not yet been
expanded, the prose immediately under the badges must override the coarse badge
and say that ordinary performance language is blocked by quotient collapse.

### 3. Summary Of Goals Behind This Evaluation

Every generated `README.md` must include a populated section titled:

```markdown
## Summary of Goals Behind this Evaluation
```

This section must appear before the one-screen verdict. It gives the reader the
why before the result.

Populate it with ordinary engineering prose that answers:

- what question this evaluation exists to answer;
- what environment or fixture is being used;
- what arms, baselines, or control conditions matter;
- what comparison is intended;
- what the evaluation is not trying to prove;
- what claim boundary should frame the rest of the report.

Do not leave this section as `[...]`, `TODO`, `TBD`, or any other placeholder.

If the source artifacts do not contain enough goal context, use the repo design
docs, checked-in evaluation readout docs, source binding, method file, and
runbook to write the best supported goal summary. If the goal still cannot be
determined, the section must still be populated with:

- the known environment/evaluation identity;
- the known run mode and source files;
- the specific missing goal context;
- a clarifying question mirrored in `Clarifying Questions And Turns`.

For the counterpoint first serious learning readout, this section should explain
that the evaluation compares direct counterpoint learning against tower-control
learning on `counterpoint_symbolic_n3_small_v001`, with direct tabular Q and
empty-schema tower as critical baselines, and with non-empty contraction schemas
tested as the real tower/control comparison. It must also state the non-goals:
not musical quality, not tensor-enabled performance, not GPU/CUDA performance,
and not a general tower-superiority claim.

### 4. Summary Of Methodology Behind This Evaluation

Every generated `README.md` must include a populated section titled:

```markdown
## Summary of Methodology Behind this Evaluation
```

This section must appear after the goal summary and before the one-screen
verdict. It gives the reader the how before the result.

Populate it with ordinary engineering prose that answers:

- what evaluation method class or comparison design is being used;
- what environment fixture is being used and why;
- what arms, baselines, controls, and comparison groups are included;
- what budget, seed policy, schema-seed policy, horizon, and replicate policy
  were used;
- which path produced the artifacts: calibration, locked run, summarize,
  readout, or another run mode;
- what artifact contract and expected-file policy apply;
- what aggregation or statistical method produced the result tables;
- what timing categories are included and excluded;
- what linearization/backend condition applies;
- what the methodology cannot support as a claim.

Do not leave this section as `[...]`, `TODO`, `TBD`, or any other placeholder.

If the source artifacts do not contain enough methodology context, use the repo
design docs, checked-in evaluation readout docs, source binding, method file,
runbook, and artifact index to write the best supported methodology summary. If
the methodology still cannot be determined, the section must still be populated
with:

- the known evaluation method facts;
- the known run mode and source files;
- the specific missing methodology context;
- a clarifying question mirrored in `Clarifying Questions And Turns`.

For the counterpoint first serious learning readout, this section should explain
that the evaluation compares direct environment arms against active-tier
exploit/explore tower-control arms under shared seed, budget, mask, artifact,
timing, and linearization discipline. It should name direct masked random,
direct tabular Q, empty-schema tower, random balanced/unbalanced tower,
structured motion tower, and bad/adversarial tower arms. It should say that the
recorded run is a locked serious-run/summarize artifact set under
`tensor_available_disabled`, with 16 episodes per run, 4 replicates, 3 random
schema seeds, and max 8 steps per episode when those facts are present in the
budget lock.

### 5. One-Screen Verdict

State the result in plain language.

The verdict must distinguish:

- artifact completion;
- behavioral success;
- benchmark claim support.

Example:

```text
All required arms produced artifacts. Direct arms and the empty tower arm
executed real environment steps and received nonzero return. The non-empty tower
arms completed artifact runs but produced zero-return, zero-step episodes due to
lift/action-realization failures. This run is therefore useful diagnostic
evidence, but it does not support a positive tower-performance claim.
```

### 6. Run Identity

Record:

- evaluation id;
- source artifact root;
- source evaluation root;
- repo readout surface;
- environment family and instance;
- run date/time if available;
- linearization mode;
- artifact schema version;
- command or runbook path;
- budget lock path if applicable.

### 7. Claim Boundary

Say exactly what the report may and may not claim.

The claim boundary must include:

- smoke, calibration, diagnostic, or serious run status;
- whether tensor execution is enabled or disabled;
- whether GPU/CUDA claims are excluded;
- whether musical-quality claims are excluded;
- whether general method superiority claims are excluded.

### 8. Arm Legend

Translate every arm id into a human label.

The legend should include:

- arm id;
- short label;
- method class;
- schema class if any;
- baseline role;
- expected interpretation.

Example labels:

```text
direct_tabular_q
Direct tabular Q baseline. Learns on concrete counterpoint states.

tower_random_balanced_exploit_explore_tabular_q
Tower controller with random balanced contraction schema. Tests whether this
schema supports action realization and learning under the tower interface.
```

### 9. Main Result Table

Do not paste the raw aggregate table as the only table.

Create a reader-facing table with:

- short arm label;
- artifact status;
- behavioral status;
- mean return;
- delta versus baseline;
- episode count;
- step count or mean step count;
- main warning;
- evidence file.

Raw statistical columns can follow in a technical appendix.

### 10. Diagnostic Findings

If any arm has surprising, zero, missing, failed, or inconsistent values, write a
diagnostic section.

This section should answer:

- what went wrong or changed;
- which artifacts show it;
- how widespread it is;
- whether it invalidates a claim;
- whether it indicates a code bug, environment fact, schema fact, or expected
  negative result.

For tower-control or quotient-schema evaluations, diagnostic findings must
include a reader-facing tower structure and tier-occupancy explanation whenever
those facts affect interpretation.

At minimum, explain:

- what each reported tower-shape tuple means, for example
  `state_cell_count_by_tier = (108, 3, 1, 1, 1)`;
- which tier index is the base/fine tier and which direction is more
  coarsened for this repo's runtime convention;
- which tiers actually received controller events;
- which tiers actually executed concrete environment steps;
- which tiers produced lift/action-realization failures and why;
- whether deeper/coarser tiers were genuinely used or merely present in the
  constructed tower.

Do not describe a tower arm as simply "better", "worse", "failed", or
"successful" without saying whether the result came from reward learning,
active-tier control, quotient shape, lift/action-realization, or missing
diagnostic evidence.

Do not describe a full or near-full first-projection collapse as ordinary
non-performance. If `pr^0_1` effectively maps the reachable hidden graph to
`pi_0(H)`, the diagnostic section must state that the runtime/environment may
be functioning exactly as constructed while the evaluation has become a
structural-limit case. In that case, the report may claim diagnostic evidence
about the schema/runtime combination, but it must block or qualify any ordinary
learner-performance, tower-advantage, or environment-non-performance claim.

### 11. Timing Readout

Timing tables must distinguish:

- total runtime;
- algorithm-online time;
- linearization setup;
- artifact logging;
- diagnostic/readout time;
- summary generation.

Do not compare methods on wall-clock timing unless the report says which timing
categories are included.

### 12. Evidence Map

End with an evidence map that tells the reader where to inspect:

- aggregate table;
- learning curves;
- timing summary;
- controller summary;
- schema diagnostics;
- run index;
- per-run event files;
- manifests;
- warnings.

The evidence map must say what each file is for.

### 12.1 Provenance Status

If any expected or commonly inspected files are absent, write a provenance
status section instead of a generic "missing evidence" section.

The provenance status must classify each absent file:

| Classification | Meaning |
| --- | --- |
| `expected_missing_gap` | The file is expected by the artifact contract for this run/evaluation and is absent. |
| `conditional_absent` | The file is expected only under a condition, such as calibration, and that condition is not established for this artifact set. |
| `not_applicable` | The file does not apply to this run mode or claim boundary. |
| `unknown_expectation` | The consultant cannot determine whether the file was expected. |

Do not use "missing" alone for files that may be conditional or not applicable.
Say what the expectation source is: source binding, blueprint, artifact
contract, CLI/run mode, or explicit Project Owner instruction.

For the counterpoint first serious learning readout, this means:

- `evaluation_manifest.json` and `evaluation_arm_manifest.json` are expected by
  the serious evaluation artifact contract; if absent, classify them as
  `expected_missing_gap`.
- `calibration_summary.json`, `calibration_run_index.csv`, and
  `calibration_recommendation.md` are calibration-path files; if the source
  artifact root is a manually locked serious run without calibration, classify
  them as `conditional_absent` or `not_applicable`, not as missing evidence.

### 13. Clarifying Questions And Turns

In `README.md`, include the protected turn surface defined above as the final
section. Do not use prose such as "No open clarifying questions recorded" in
place of the turn-pad. Empty turn slots should be represented by `> ...`.

On first generation, create the three blank turn pairs. On subsequent
generations, preserve the section intact, except to append blank turn pairs when
the section is missing, malformed, or has no blank pair available for future
conversation.

## All-Cases Protocol

Use this protocol whenever translating artifact tables to readable documents.

### Case 1: No Artifacts Found

Readable statement:

```text
No source artifacts could be resolved for this repo readout surface.
```

Required content:

- repo readout surface checked;
- source binding status;
- source artifact root checked, if known;
- source evaluation root checked, if known;
- expected files;
- absent files classified as `expected_missing_gap`, `conditional_absent`,
  `not_applicable`, or `unknown_expectation`;
- command to generate artifacts if known.

Forbidden:

- implying failure of the method;
- inventing a status;
- filling with placeholder performance text.

### Case 2: Smoke Run

Readable statement:

```text
This is a smoke run. It validates command execution and artifact writing only.
```

Required content:

- command run;
- artifact files written;
- pass/fail status;
- explicit non-claim boundary.

Forbidden:

- comparing performance as benchmark evidence;
- calling it "serious";
- using smoke results in method claims.

### Case 3: Calibration Run

Readable statement:

```text
This calibration estimates budget, runtime, artifact volume, noise, completion,
and failure modes. It is not the final result unless the Project Owner says so.
```

Required content:

- measured runtime;
- artifact volume;
- completion rate;
- curve-noise proxy if present;
- lift or controller failure indicators if present;
- proposed locked budget.

Forbidden:

- treating calibration as final evidence;
- hiding failure signals because the calibration status is complete.

### Case 4: Complete Artifact Run, Behavior Successful

Readable statement:

```text
Artifacts are complete and the behavior being measured succeeded.
```

Required content:

- completion evidence;
- behavioral success metric;
- baseline comparison;
- uncertainty or replicate count;
- claim boundary.

Forbidden:

- overclaiming beyond the benchmark condition;
- omitting the baseline.

### Case 5: Complete Artifact Run, Behavior Failed

Readable statement:

```text
Artifacts are complete, but the measured behavior failed.
```

Required content:

- which arms failed behaviorally;
- which fields show failure;
- which diagnostic rows explain failure;
- whether the failure is an implementation bug, schema limitation, controller
  limitation, or unresolved;
- whether the report is evidence against a claim or only diagnostic evidence.

This is the case that raw tables often hide.

Example signs:

- `status=complete` but `mean_return=0.0`;
- `success=False`;
- `step_count=0`;
- repeated invalid lift/action failures;
- controller events never reach execution;
- missing or empty final state.

### Case 6: Mixed Run

Readable statement:

```text
Some arms succeeded and others failed. The result must be interpreted arm by
arm.
```

Required content:

- per-arm status;
- per-arm behavioral status;
- grouped warnings;
- whether any baseline is missing;
- whether comparisons remain valid.

Forbidden:

- one global "success" label that hides failed arms;
- averaging failed and successful conditions without explanation.

### Case 7: Incomplete Run

Readable statement:

```text
The run is incomplete. Interpret available rows only as partial evidence.
```

Required content:

- completed arm count;
- missing arms;
- failed arms;
- absent files with expectation classification;
- whether rerun/resume is possible.

Forbidden:

- presenting partial tables as final;
- using missing arms as zero unless the artifact explicitly records zero.

### Case 8: Missing Baseline

Readable statement:

```text
The baseline needed for the intended comparison is missing.
```

Required content:

- intended baseline;
- missing artifact or arm;
- comparisons blocked;
- any still-readable descriptive metrics.

Forbidden:

- computing deltas against another arm without saying the baseline changed.

### Case 9: Zero Values

Zero is never self-explanatory.

For each zero in a primary metric, classify it as:

- legitimate measured zero;
- missing converted to zero;
- failed behavior converted to zero;
- impossible/unexpected zero;
- unresolved.

Required content:

- evidence for the classification;
- files inspected;
- effect on claim boundary.

### Case 10: Empty Values, Nulls, NaNs

Readable statement:

```text
Some fields were not produced or are not applicable.
```

Required content:

- whether empty means not applicable, missing, failed, or not computed;
- whether downstream statistics were skipped;
- whether the result remains interpretable.

Forbidden:

- treating null and zero as the same thing.

### Case 11: Outliers Or High Variance

Readable statement:

```text
The result varies substantially across seeds, schema seeds, or replicates.
```

Required content:

- which variance column shows it;
- whether variation is across environment seeds, schema seeds, or episodes;
- whether more runs are needed before a claim.

### Case 12: Timing Result

Readable statement:

```text
The timing result applies only to the recorded timing categories.
```

Required content:

- included categories;
- excluded categories;
- whether artifact logging is included;
- whether setup time is included;
- whether linearization setup is included.

Forbidden:

- presenting total runtime as algorithm speed without category explanation.

### Case 13: Diagnostic-Only Result

Readable statement:

```text
This result diagnoses structure or mechanism. It is not a learning-performance
claim.
```

Required content:

- diagnostic target;
- relevant counts/rates;
- what would count as healthy or unhealthy;
- whether it blocks a performance claim.

### Case 14: Claim-Supporting Result

Readable statement:

```text
This result supports only the claim named below.
```

Required content:

- exact claim;
- baseline;
- budget;
- seed policy;
- environment fixture;
- linearization/backend condition;
- uncertainty;
- known exclusions.

Forbidden:

- generalizing from one fixture to all environments;
- generalizing from tensor-disabled to tensor-enabled;
- claiming musical quality from reward tables alone.

## Field Translation Rules

Raw field names must be translated when exposed to human readers.

Use a glossary or inline labels for fields such as:

- `arm_id`;
- `mode_id`;
- `schema_id`;
- `schema_seed`;
- `seed_bundle_id`;
- `mean_return`;
- `delta_vs_direct_tabular_q`;
- `delta_vs_empty_tower`;
- `schema_seed_return_std`;
- `control_action`;
- `active_tier_before`;
- `active_tier_after`;
- `failure_reason`;
- `linearization_mode_id`.

Do not assume readers know whether a field is:

- identity metadata;
- budget metadata;
- statistical output;
- behavioral output;
- diagnostic output;
- claim-boundary metadata.

## Status Translation Rules

Never use a single status field as the whole result.

Every report must separate:

```text
artifact_status
behavior_status
claim_status
```

Suggested meanings:

```text
artifact_status:
  missing
  incomplete
  complete

behavior_status:
  not_run
  succeeded
  failed
  mixed
  structural_limit
  diagnostic_only
  unresolved

claim_status:
  no_claim
  smoke_non_evidence
  calibration_only
  diagnostic_evidence
  supports_limited_claim
  blocks_claim
  unresolved
```

If the machine artifact has only `status=complete`, the readable document must
still infer and state whether behavior succeeded or failed.

If behavior is table-mixed but the dominant explanation is quotient collapse,
lift-realization, or another structural limit, do not stop at
`behavior_status=mixed`. Use `structural_limit` or `diagnostic_only`, and state
the narrower mixed facts as supporting detail.

## Evidence Discipline

Readable documents must include enough evidence for audit.

For every important interpretation, include:

- the source table or file;
- the relevant field names;
- the observed value or pattern;
- the conclusion drawn;
- the confidence or uncertainty.

Bad:

```text
The tower arms failed.
```

Better:

```text
The non-empty tower arms completed artifact runs but failed behaviorally:
their aggregate rows have mean_return 0.0, their episode rows have step_count 0
and success False, and their lift-fiber event rows repeatedly record
invalid_action_index.
```

## Claim Boundary Discipline

A readable document must say what it does not prove.

Common non-claims:

- not a tensor-enabled result;
- not a CUDA/GPU result;
- not a musical-quality result;
- not a general superiority result;
- not a production performance result;
- not a claim beyond the named fixture;
- not a claim beyond the named budget.

If a failure occurs, do not hide it behind the non-claim boundary. State both:

```text
This does not prove X.
It does show Y failed under this run condition.
```

## Required Output Files

For a serious evaluation, prefer this generated human-facing set:

```text
<repo-readout-surface>/
  readout_source.json
  README.md
  result_readout.md
  runbook.md
  artifact_index.md
  glossary.md
  results/
    summary.md
    human_summary.md
    arm_readout_table.md
    diagnostic_findings.md
    timing_readout.md
```

The exact repo folder may vary by evaluation, but the command target and output
home are the same repo-side readout surface. Raw artifact roots are evidence
sources, not output homes.

## Minimum Acceptable Human Report

If time is short, the minimum acceptable human-readable report is:

1. summary of goals behind the evaluation;
2. summary of methodology behind the evaluation;
3. one-screen verdict;
4. arm legend;
5. reader-facing result table;
6. diagnostic warnings;
7. claim boundary;
8. evidence map.

Anything less is an artifact index, not a result report.

## Stop Conditions

Stop and ask the Project Owner before writing a claim if:

- a table says complete but behavior looks failed;
- a primary metric is zero and the reason is unclear;
- a baseline is missing;
- a run is partial;
- a field meaning is ambiguous;
- two artifacts disagree;
- the result would require a claim not approved in design docs;
- interpreting the result requires a domain judgment the Project Owner has not
  authorized.

## Operating Summary

When turning benchmark tables into readable docs:

```text
Do not merely list files.
Do not merely paste tables.
Do not let complete mean successful.
Do not let zero pass unexplained.
Do not hide diagnostics in appendices.
Do not make claims from artifacts alone.

Translate ids into names.
Translate statuses into artifact/behavior/claim state.
Translate metrics into meaning.
Translate anomalies into explicit warnings.
Translate every conclusion back to evidence.
```

The machine artifacts are the source of truth.

The human document is the source of understanding.
