# Git Practices

## Status

This document is a prime-directive adjunct devoted specifically to git discipline in this repository.

It exists to capture git policies that are operational rather than merely stylistic.

Its purpose is to reduce:

- state confusion
- merge confusion
- branch-discipline drift
- and execution-history ambiguity

when implementation work is being carried out under blueprint/workplan authority.

## Rule 1

> **When a blueprint and an associated implementation workplan have been written and approved, execution should begin on a dedicated implementation branch rather than directly on `main`.**

### Required workflow

The required workflow is:

1. a blueprint is written
2. an associated implementation workplan is written
3. the Project Owner approves execution
4. before implementation begins, move to a dedicated implementation git branch
5. execute implementation work there
6. validate there
7. merge back afterward

### Why this rule exists

This rule exists because implementation directly on `main` creates several avoidable problems:

- it blurs the distinction between approved history and in-progress working-tree edits
- it makes later merge discussion confusing or impossible
- it weakens rollback clarity
- it makes it harder to tell what work belongs to a particular blueprint/workplan execution interval
- it increases the risk of mixing unrelated local modifications with the implementation interval

### What this rule is trying to preserve

This rule preserves:

- clean implementation lineage
- explicit merge points
- easier review and validation
- clearer continuity reporting
- lower confusion about whether work is:
  - only in the worktree
  - committed on a branch
  - or merged into `main`

### Operational interpretation

This rule does **not** mean that every tiny edit in the repo requires a branch.

It applies specifically when the work has the form:

- blueprint
- associated implementation workplan
- explicit execution interval

That is the level at which branch discipline becomes part of execution discipline.

### Default branch naming expectation

Unless the Project Owner requests otherwise, the implementation branch should use the normal Codex branch prefix and a task-specific suffix, for example:

- `codex/<implementation-topic>`

### Summary

The operational summary is:

> **Approved blueprint + approved workplan + execution request => create/switch to an implementation branch before touching implementation code.**

