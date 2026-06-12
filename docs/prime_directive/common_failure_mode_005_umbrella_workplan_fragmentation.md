# Common Failure Mode 005: Umbrella Workplan Fragmentation

## Status

Mandatory operational warning for future Embedded Engineering Consultants
working in this repository.

This document exists because an umbrella evaluation suite was designed with a
parent workplan and multiple child workplans, but the LLM treated each child
workplan as a separate endpoint. That forced the Project Owner to repeatedly
restart or redirect the LLM stage-by-stage even though the intended unit of
work was the whole umbrella suite.

That behavior is unacceptable when the Project Owner has approved or requested
the umbrella job.

## Incident Class

The failure class is:

```text
fragmenting an umbrella workplan into manually restarted child workplans
```

The specific observed form was:

```text
complete child Stage N
report that child Stage N+1 is next
stop and wait for the Project Owner to manually restart child Stage N+1
```

This created repeated resume confusion and made the Project Owner carry the
execution spine that should have been encoded in the parent workplan.

## Core Rule

> If the Project Owner asks to build, execute, resume, or finish a whole
> umbrella workplan, child workplans are checkpoints, not endpoints.

The LLM must continue through the ordered child workplans until the umbrella
work is complete, unless a true stop condition occurs.

## Parent Workplan Authority

When a parent folder or parent workplan organizes child workplans, the LLM must
distinguish:

```text
execute this one child component
```

from:

```text
execute the whole umbrella system
```

If the Project Owner asks for the whole umbrella system, the parent workplan
becomes the active execution spine.

The LLM must not treat child workplans as independent jobs that each require
fresh Project Owner initiation unless the Project Owner explicitly requested
that pacing.

## Required Continuation Behavior

When executing an umbrella workplan, after a child workplan completes, the LLM
must:

1. update the child implementation log;
2. identify the next child workplan from the parent sequence;
3. verify the next child gate using repo artifacts and readout sources;
4. continue to the next child workplan;
5. record any blocker in the current implementation log.

The LLM may give a short progress update, but it must not stop merely because a
child component ended.

## True Stop Conditions

The LLM must stop only if:

- the Project Owner explicitly says stop, pause, or switch topics;
- the next child workplan contains an unresolved Project Owner decision;
- the gate into the next child fails and cannot be repaired under the current
  approved workplan;
- a required artifact, readout source, or manifest is missing or contradictory;
- continuing would overwrite or confuse unrelated dirty work;
- implementation would require a workplan rewrite, scope reduction, or
  consultant-authored design decision not approved by the Project Owner.

Absent one of these conditions, the next child workplan should be executed
without requiring a new Project Owner prompt.

## Stage Terminology Guard

Many repository workplans use `Phase.Stage.Action` discipline.

Umbrella suites may also use "Stage" to mean a child evaluation component.

These are not the same thing.

When both meanings are live, the LLM must write:

```text
gauntlet Stage 5
child Stage 5
Phase 2.Stage 1.Action 3
```

and must avoid bare phrases like:

```text
Stage 5
```

when the meaning could be ambiguous.

## Forbidden Behaviors

The LLM must not:

- complete a child workplan and stop without a true stop condition;
- ask the Project Owner to manually reissue the next child workplan when the
  parent workplan already orders it;
- frame the next child as a new project when it is part of the approved
  umbrella job;
- report "we are ready for child Stage N+1" as a final answer if the correct
  action is to continue into child Stage N+1;
- confuse `Phase.Stage.Action` stages with umbrella child stages;
- use a generated README conversation as the only execution spine when a parent
  workplan exists.

## Required Parent Workplan Content

Future umbrella workplans should include a section named:

```text
Umbrella Execution Spine
```

That section must define:

- the ordered child workplans;
- whether child completion is a stop point or checkpoint;
- the current resume point, if execution is already underway;
- true stop conditions;
- the final readout/regeneration step;
- terminology distinguishing child stages from `Phase.Stage.Action` stages.

## Relationship To Other Failure Modes

This failure mode is adjacent to but distinct from:

- workplan rewrite during implementation;
- implementation without owner approval;
- false attribution.

Umbrella fragmentation does not necessarily rewrite a child workplan. Instead,
it loses the parent control structure that made the child workplans one coherent
job.

## Operational Summary

The correct operational rule is:

> **Whole umbrella requested = parent workplan is the execution spine. Child
> workplans continue until the umbrella is complete or a true stop condition
> occurs.**

Not:

> "Finish one child, then wait for the human to rediscover and reissue the next
> child."
