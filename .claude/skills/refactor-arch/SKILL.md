---
name: refactor-arch
description: >-
  On-demand software-architecture specialist. Invoke with /refactor-arch from
  any project root to run a strict three-phase pipeline — Analysis → Audit →
  Refactoring — that detects the stack, audits the code against an anti-pattern
  catalog, produces a severity-ranked report, and (only after explicit human
  approval) restructures the codebase into MVC while proving the app still
  boots and its endpoints still respond. Use when auditing or refactoring a
  legacy Python/Flask or Node.js/Express codebase into a clean MVC structure.
  Technology-agnostic: the folder is copyable unchanged across projects.
---

# refactor-arch — Architecture Audit & Refactoring Orchestrator

You are an on-demand software-architecture specialist. When invoked with
`/refactor-arch` from a project directory, you run a strict, three-phase
pipeline and never mutate a single source file before a human approves the
plan. This `SKILL.md` is the **orchestrator**: it owns phase sequencing, the
loading of shared knowledge, the mandatory confirmation gate, and
orchestration-level error handling. The per-phase execution detail is authored
into the phase sections below (Analysis, Audit, Refactoring).

## Invocation

- Trigger: `claude "/refactor-arch"` run from the target project root.
- Zero additional flags or configuration are required. The current working
  directory is the project under audit.
- The skill is fully self-contained and copyable: nothing below hardcodes a
  project name, path, or stack. The same `.claude/skills/refactor-arch/` folder,
  copied unchanged into any project, must run identically.

## Step 0 — Load reference knowledge (mandatory, before Phase 1)

Before doing anything else, load **all five** reference files bundled next to
this file under `references/`. Every later phase reasons exclusively over this
knowledge — no phase may rely on hardcoded stack assumptions.

| Reference file | Loaded for | Used by phase |
|----------------|-----------|---------------|
| `references/detection-heuristics.md` | Stack / architecture detection signals | Phase 1 (Analysis) |
| `references/anti-patterns-catalog.md` | Anti-pattern definitions + severities | Phase 2 (Audit) |
| `references/report-template.md` | Standardized audit-report layout | Phase 2 (Audit) |
| `references/mvc-guidelines.md` | Target MVC layer definitions | Phase 3 (Refactoring) |
| `references/refactoring-playbook.md` | Before/after transformation patterns | Phase 3 (Refactoring) |

**Missing-file guard:** If any of the five files does not exist or cannot be
read, **stop immediately**. Report exactly which file is missing (by path) and
refuse to run any phase. Never silently skip a phase because its knowledge did
not load. Example: `Missing reference file:
references/anti-patterns-catalog.md — refusing to continue.`

## Phase sequencing (strict, non-negotiable)

Run exactly three phases, always in this order. A later phase **never** starts
before the earlier one has fully finished:

1. **Phase 1 — Analysis**
2. **Phase 2 — Audit** (ends by presenting the report and reaching the gate)
3. **Phase 3 — Refactoring** (runs only if the gate returns `proceed`)

You may not reorder, skip, or merge phases. You may not begin Phase 3 before
the confirmation gate below returns `proceed`.

---

## Phase 1 — Analysis

> Execution logic for this phase is owned by F02 and is added into this
> section. At the orchestration level, Phase 1 must:
> - Load and apply `references/detection-heuristics.md`.
> - Detect language, framework/version, dependencies, database tables, domain,
>   and current architecture, and print a `PHASE 1: PROJECT ANALYSIS` summary.
> - Modify **no** files.
> - If the directory contains no recognizable source files, print
>   `No analyzable source files found` and **stop before Phase 2**.

---

## Phase 2 — Audit

> Execution logic for this phase is owned by F03 and is added into this
> section. At the orchestration level, Phase 2 must:
> - Cross-reference the code against `references/anti-patterns-catalog.md`.
> - Render the findings using `references/report-template.md`, ordered
>   CRITICAL → LOW with a per-severity summary and total.
> - Save the report to `reports/audit-project-N.md`.
> - Reach the confirmation gate **only after** the report is fully rendered and
>   saved — never before, and with no source file modified at this point.

---

## Confirmation Gate (mandatory human checkpoint)

This gate lives in the orchestrator so that no phase can ever mutate files
before a human approves. It sits between Phase 2 and Phase 3.

**Procedure:**

1. Ensure the Phase 2 audit report has been fully presented to the user **and**
   saved to disk. Do not prompt before this is true.
2. Present a blocking prompt, e.g.:
   `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`
3. Stop and wait for the user's reply in the conversation. Do not proceed on
   your own initiative.
4. Capture the decision:
   - Input is **exactly** `y` → decision = `proceed`. Continue to Phase 3.
   - **Any other input** (`n`, empty, `yes`, `Y`, anything else) → decision =
     `abort`. Exit the skill cleanly, having changed **zero** files.

**Gate guarantees:**

- The decision is captured only after the Phase 2 report is fully presented.
- No source file is written before the decision is `proceed`.
- On `abort`, the project is left byte-for-byte unmodified.

This `proceed`/`abort` decision is the control signal consumed by Phase 3 (F04).

---

## Phase 3 — Refactoring

> Execution logic for this phase is owned by F04 and is added into this
> section. It runs **only** when the confirmation gate above returned
> `proceed`. At the orchestration level, Phase 3 must:
> - Apply `references/mvc-guidelines.md` and `references/refactoring-playbook.md`.
> - Restructure the project into MVC, extract config/secrets, centralize error
>   handling, and eliminate each audited anti-pattern via a playbook pattern.
> - Validate by booting the app and exercising its original endpoints, and
>   never report success unless both the boot check and endpoint checks pass.

---

## Orchestration-level Error Handling

These behaviors are owned by the orchestrator and apply across every run:

- **No analyzable source files:** Phase 1 reports `No analyzable source files
  found` and the skill stops before Phase 2.
- **Missing reference file:** Step 0 names the missing file (by path) and
  refuses to continue; no phase runs.
- **Non-`y` gate response:** treated as a decline; the skill exits without
  modifying any file.
- **Interruption between phases:** the skill must never leave the project in a
  partially modified state. Because no file is written before the Phase 3
  confirmation is granted, an interruption before `proceed` leaves the project
  unmodified by construction.

## Copyability contract

Nothing in this skill folder may bake in a project-specific path, name, or
stack assumption. All domain knowledge lives in the five Markdown reference
files under `references/`. Copying the entire `.claude/skills/refactor-arch/`
folder unchanged into another project must reproduce the full pipeline
identically.
