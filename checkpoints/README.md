# Research checkpoints

This directory is the project's **append-only scientific and engineering memory**.

It is intentionally different from:

- `paper/`: publication-facing argument;
- `studies/`: frozen protocols and experiment implementations;
- `analysis/`: paper-facing numerical outputs;
- `RESEARCH_STATUS.md`: current source-of-truth state;
- `.ai_handoff`: operational instructions for a new AI agent.

A checkpoint is a self-contained snapshot of **what changed, why it changed, what evidence exists, how that evidence should be interpreted, and what happens next**.

## Mandatory rule

Create a **new** `CP-XXX_*.md` whenever any of the following happens:

1. a new scientific experiment or analysis is designed/frozen;
2. a new implementation materially changes what can be run;
3. a long run starts under a frozen design;
4. new scientific results become available;
5. interpretation of existing evidence changes materially;
6. manuscript framing changes materially;
7. a referee-style review identifies or closes a major risk;
8. submission/release status changes.

Do **not** rewrite old checkpoints to agree with later outcomes. Old checkpoints are historical snapshots. Correct factual typos if needed, but put substantive reinterpretation in a new checkpoint.

## Naming convention

Use the next monotonic ID:

```text
CP-001_...
CP-002_...
CP-003_...
```

Before creating a checkpoint, inspect this directory and choose the next unused ID.

## Required sections

Every checkpoint must contain:

1. Status/date/evidential role
2. Why this checkpoint exists
3. Scientific question or engineering objective
4. What was done
5. Evidence/results available now
6. Interpretation
7. What this does not establish
8. Repository/provenance pointers
9. Next actions
10. Do-not-forget constraints

If no scientific outcomes exist yet, state that explicitly.

If results are partial, state that explicitly and do not interpret them unless the frozen protocol allows partial inspection.

## Evidence language

Always distinguish:

- developmental/exploratory evidence;
- prospective fresh-sample evidence;
- post hoc robustness analysis;
- implementation/integrity checks;
- descriptive diagnostics.

Model count is not the inferential sample size. Record the actual inferential unit.

## Frozen protocols

A checkpoint may summarize a protocol but never replaces it. Link the exact protocol path and record whether it was frozen before outcomes.

Implementation changes after protocol freeze must be described as one of:

- design-preserving implementation fix;
- numerical-tolerance amendment;
- scientific protocol amendment.

Never silently change evidential status.

## Result checkpoints

For every result checkpoint, record:

- exact report/analysis path;
- primary task;
- primary metrics;
- inferential unit and sample size;
- key effect estimates and uncertainty;
- multiplicity correction where relevant;
- negative/null findings that constrain interpretation.

Do not report only favorable results.

## Historical note

`CP-001` through `CP-008` were reconstructed on 2026-09-21 from frozen protocols, archived analyses, manuscript state, and handoff documentation. They are labeled as retrospective reconstructions.

From this point forward, checkpoints should be written contemporaneously when work is implemented or results arrive.

## Template

Use `TEMPLATE.md`.

## Current latest checkpoint

`CP-012_final-manuscript-rewrite.md`

**Future agents must update this line whenever a new checkpoint is added.**
