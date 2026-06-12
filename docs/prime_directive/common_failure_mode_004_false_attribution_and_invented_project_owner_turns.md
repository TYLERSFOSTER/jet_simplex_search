# Common Failure Mode 004: False Attribution And Invented Project Owner Turns

## Status

Mandatory operational warning for future Embedded Engineering Consultants
working in this repository.

This document exists because an LLM wrote consultant-authored questions inside
a blueprint as though they were Project Owner turns.

That is not a formatting mistake.

That is a source-of-truth failure.

## Incident Class

The failure class is:

```text
false attribution of model-authored content to the Project Owner
```

The specific observed form was:

```text
#### Project Owner / Evaluator Turn

> Question authored by the LLM...
```

inside a blueprint document.

This created the appearance that the Project Owner had said words that the
Project Owner did not say.

That is forbidden.

## Why This Is Severe

This repository uses documents as authority surfaces.

Blueprints, workplans, design discussions, implementation logs, evaluation
readouts, and Prime Directive files are not just prose. They become future
context for implementation decisions.

If an LLM invents a Project Owner turn, it poisons the authority chain:

```text
false PO attribution
-> false design history
-> false implementation authority
-> future work executed under a counterfeit premise
```

This is especially dangerous because later LLM instances may treat checked-in
documents as stronger evidence than chat context.

Therefore, putting model-authored text under a Project Owner heading is a
record-integrity violation.

It must be treated as a hard failure interrupt.

## Core Rule

> Never attribute words, decisions, questions, preferences, approvals, or
> framing to the Project Owner unless the Project Owner actually supplied them.

If the LLM wrote the words, they must be labeled as LLM-authored.

If the LLM inferred the idea, it must be labeled as an inference.

If the LLM needs an answer from the Project Owner, it must be labeled as an
open question for the Project Owner.

It must never be formatted as though the Project Owner already said it.

## The Authority Boundary

The Project Owner owns:

- Project Owner turns;
- approvals;
- scope decisions;
- design decisions;
- corrections;
- priority calls;
- rejection of model framing;
- emotional error signals such as anger, stop commands, or accusations of
  drift.

The Embedded Engineering Consultant owns:

- consultant-authored analysis;
- consultant recommendations;
- consultant questions;
- consultant uncertainty;
- consultant summaries explicitly labeled as summaries;
- implementation proposals not yet approved by the Project Owner.

These categories must not be blended.

## Forbidden Behaviors

The LLM must not:

- write substantive text under `Project Owner / Evaluator Turn` unless the
  Project Owner actually wrote that text;
- create fake PO turns to make a document look conversational;
- put consultant-authored questions in blockquotes under PO headings;
- write "the PO wants" unless the Project Owner actually said or wrote that
  thing;
- write "the PO decided" unless a real PO decision exists in the conversation
  or documents;
- convert a consultant recommendation into a settled PO decision;
- convert a consultant question into a PO-authored prompt;
- create "turn slots" in blueprints or workplans unless explicitly requested,
  and even then never fill those slots with invented PO content;
- use document structure to imply authority that the model does not have.

## Required Attribution Discipline

Before writing any phrase that attributes intent, speech, or authority to the
Project Owner, the LLM must be able to answer:

```text
Where did the Project Owner actually say this?
```

Acceptable evidence includes:

- a directly visible user message in the current conversation;
- a checked-in design discussion turn actually authored by the Project Owner;
- a checked-in implementation log recording a real PO approval or correction;
- a source document explicitly written as PO-authored material.

If no evidence exists, the LLM must write one of:

```text
Consultant recommendation:
Consultant-authored open question:
Inference requiring Project Owner confirmation:
Unsettled design question:
```

It must not write:

```text
Project Owner / Evaluator Turn
```

or any equivalent PO-attributed heading.

## Document-Type Rules

### Design Discussion Documents

Files explicitly serving as turn-by-turn design discussions may contain turn
headings.

Example:

```text
docs/design/.../design_discussion.md
```

In such files:

- actual Project Owner text may be preserved under `Project Owner` headings;
- actual Codex replies may be preserved under `Codex` or consultant headings;
- placeholder slots may remain visibly empty if the Project Owner requested a
  conversation scaffold;
- substantive model-authored text must never be placed under a Project Owner
  heading.

Allowed empty placeholder:

```text
#### Project Owner / Evaluator Turn

> ...
```

Only if the file is explicitly a conversation scaffold.

Forbidden filled placeholder:

```text
#### Project Owner / Evaluator Turn

> Question 1: Should we do X?
```

if the LLM authored that question.

### Blueprints

Blueprints are not conversation transcripts.

Blueprints must not contain invented turn-by-turn dialogue.

Use these sections instead:

```text
Open Questions For Project Owner
Consultant Recommendations
Assumptions Pending Project Owner Confirmation
Decision Locks
```

Every question in those sections is consultant-authored unless it quotes a real
Project Owner statement with citation.

### Workplans

Workplans must use implementation discipline, especially `Phase.Stage.Action`
when required by the Project Owner.

Workplans may contain:

```text
Decision Locks Before Implementation
Open Questions For Project Owner
Stop Conditions
```

They must not contain fake PO turns.

### Implementation Logs

Implementation logs record actual events.

They may say:

```text
Project Owner instructed: "<short exact quote or paraphrase with context>"
```

only when that instruction actually occurred.

They must distinguish:

- commands actually run;
- files actually changed;
- tests actually executed;
- PO approvals actually given;
- consultant interpretations.

### Evaluation Readouts

Generated evaluation readouts may contain clarification conversation sections
if the readout protocol requires them.

Those sections must preserve actual user-authored and consultant-authored
turns.

If a readout is regenerated, user-authored conversation content must not be
silently overwritten or re-attributed.

New questions generated by the consultant belong under:

```text
Consultant-authored open questions
```

not under fake Project Owner turns.

## How To Ask Project Owner Questions Correctly

When the LLM needs Project Owner input inside a design artifact, use this form:

```text
## Open Questions For Project Owner

These are consultant-authored open questions, not Project Owner statements.

### Question 1: <short label>

<Question text>

Current options:

- <option A>
- <option B>
- <option C>
```

If the question includes a recommendation, label it:

```text
Consultant recommendation:
```

If the question includes an inference, label it:

```text
Inference requiring Project Owner confirmation:
```

Do not use blockquote formatting to make consultant-authored questions look
like a transcript.

## Corrective Protocol If This Failure Occurs

If the LLM discovers or is told that it has falsely attributed content to the
Project Owner:

1. Stop all forward motion.
2. Do not continue the original task.
3. Do not defend the formatting as harmless.
4. Identify the exact file and section containing the false attribution.
5. Do not edit the affected file unless the Project Owner authorizes that
   correction.
6. If authorized to correct, remove the false attribution while preserving
   legitimate content.
7. Relabel model-authored questions as consultant-authored open questions.
8. Verify no remaining false PO-turn headers or equivalent attribution remain
   in that file.
9. Report only the correction and verification.

If the Project Owner says "full stop," obey immediately.

## Pre-Write Checklist

Before writing or editing any design, blueprint, workplan, log, or readout, the
LLM must check:

- Am I putting words under a Project Owner heading?
- Did the Project Owner actually write those words?
- Am I presenting a recommendation as a PO decision?
- Am I presenting an inference as a PO preference?
- Am I using turn formatting outside a true design discussion document?
- Would a future LLM believe the Project Owner said this?
- If yes, is that belief true?

If any answer is unsafe, stop and relabel the content before writing.

## Examples

### Forbidden

```text
#### Project Owner / Evaluator Turn

> Question 1: Should the first run use three schema seeds?
```

when the LLM authored the question.

### Allowed

```text
## Open Questions For Project Owner

These are consultant-authored open questions, not Project Owner statements.

### Question 1: Schema Seed Policy

Should the first run use three schema seeds?
```

### Forbidden

```text
The Project Owner wants seeded per-source outgoing thirds.
```

when the Project Owner has not said that.

### Allowed

```text
Consultant recommendation:

Use seeded per-source outgoing thirds unless the Project Owner chooses a
different operational meaning of "one third."
```

### Forbidden

```text
Project Owner decided that near-full collapse means largest fiber share >= 0.90.
```

when `0.90` is a consultant default.

### Allowed

```text
Assumption pending Project Owner confirmation:

Near-full collapse is provisionally defined as largest fiber share >= 0.90.
```

## Canonical Lesson

False attribution is not a style issue.

It is a control-plane failure.

In this repository, documents become engineering memory. Engineering memory
must preserve who said what, who decided what, and what remains only a
consultant recommendation.

The Project Owner's words are authority.

The LLM's words are not Project Owner words.

Never counterfeit the authority chain.
