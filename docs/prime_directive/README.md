# Prime Directive Protocol Map

This folder contains operating protocols directed to the Embedded Engineering
Consultant.

The benchmark workflow is:

```text
1. Construct an environment.
2. Construct evaluations for that environment.
3. Process run artifacts into repo-side human-readable readouts.
```

Use these protocol documents for that workflow:

- `environment_construction_for_benchmark_evaluations_protocol.md`
- `evaluation_construction_for_readable_artifacts_protocol.md`
- `artifact_table_to_readable_document_protocol.md`
- `public_release_readiness_protocol.md`

The core collaboration and execution discipline lives in:

- `prime_directive.md`
- `git_practices.md`
- `common_failure_mode_001.md`
- `common_failure_mode_002_implementation_without_owner_approval.md`
- `common_failure_mode_003_gameplan_rewrite_during_implementation.md`
- `common_failure_mode_004_false_attribution_and_invented_project_owner_turns.md`
- `common_failure_mode_005_umbrella_workplan_fragmentation.md`

When an approved parent workplan organizes multiple child workplans, treat the
parent workplan as the execution spine if the Project Owner asks to build,
execute, resume, or finish the whole umbrella system. Child workplan completion
is then a checkpoint, not an automatic stop. Continue to the next child workplan
unless a true stop condition from
`common_failure_mode_005_umbrella_workplan_fragmentation.md` occurs.

When the Project Owner asks for a human-readable run report, remind them of the
explicit protocol/source-binding command:

```text
execute docs/prime_directive/artifact_table_to_readable_document_protocol.md at docs/evaluations/<environment>/<evaluation>/readout_source.json
```

The file in that command is the checked-in source binding. It is not the README,
the raw artifact root, or the raw evaluation root. Generated evaluation READMEs
should begin with local two-segment SVG status badges and a compact
`Status At A Glance` section derived from the same evidence as the detailed
readout. Badge text must be reader-facing `Label: Value` text, not raw
`snake_case` machine statuses.

For durable serious evaluations, raw artifact tables should also be generated
inside the repo readout surface under `artifacts/<run-label>/`, so the
checked-in readout is bound to repo-resident evidence rather than a temporary
local path.

For public beta/release preparation, also run:

```bash
uv run python scripts/release_hygiene.py --repo-root .
```

Public release hygiene uses repo-relative paths, `[XXX]` public redaction,
verified artifact bundles for large raw artifacts, and explicit stop
conditions before irreversible release actions.
