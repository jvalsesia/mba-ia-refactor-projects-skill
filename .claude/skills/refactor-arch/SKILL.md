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

Phase 1 detects the stack and architecture of the project rooted at the current
working directory, then prints a fixed-format `PHASE 1: PROJECT ANALYSIS`
summary that Phase 2 reasons over. It is **strictly read-only**: it modifies no
file. All detection knowledge comes from `references/detection-heuristics.md`
(loaded in Step 0) — **never** from hardcoded stack assumptions baked into this
phase.

### 1.1 — Load detection knowledge

Use `references/detection-heuristics.md` as the **sole** source of detection
signals. That file defines six detection categories (Language, Framework /
version, Dependencies, Database / tables, Domain, Architecture), each as a
*signal → conclusion* pairing. Apply those signals; do not invent stack-specific
rules that are not expressed there. If Step 0 could not load this file, the
Missing-file guard has already stopped the run.

### 1.2 — Apply the six detection categories to the CWD

Walk the current working directory and apply each heuristic category in order.
Prefer concrete file/content signals over guesses; when signals conflict, report
the strongest evidence and note the ambiguity rather than assuming.

1. **Language** — Glob the tree for source extensions per the heuristics'
   Language table, count each, and pick the dominant language. Record the count
   for the analyzed-file total below.
2. **Framework + version** — Match the framework signals (import statements,
   manifest entries) and read the pinned version from the dependency manifest.
   Report a range verbatim if a range is given; report `version unknown` if no
   version is pinned.
3. **Dependencies** — Parse the declared **direct** dependencies from the
   manifest (`requirements.txt` / `pyproject.toml` / `Pipfile` for Python;
   `package.json` `dependencies`/`devDependencies` for Node.js). Report the
   declared list, not the full transitive tree.
4. **Database / tables** — Scan for SQL (`CREATE TABLE`, `.sql` files, migration
   folders), ORM models (SQLAlchemy `__tablename__`, Sequelize
   `sequelize.define`, Django `models.Model`), and raw drivers. Report each
   detected table/entity by name.
5. **Domain** — Infer the application domain from route paths, model names, and
   table names (not filenames alone). Report a short phrase plus the key
   entities.
6. **Architecture** — Inspect layer separation and report the high-level
   structure (monolithic / partial layering / MVC-like), per the heuristics'
   Architecture category.

**Accurate analyzed-file count.** Count source files of the detected language
under the project root, **excluding** dependency/vendor directories
(`node_modules`, `venv`, `.venv`, `.git`), lockfiles, and documentation. The
reported count must equal the real number of detected-language source files a
reviewer would find. Keep the list of scanned files so it can be printed.

### 1.3 — Emit the analysis summary

Print a summary block titled **exactly** `PHASE 1: PROJECT ANALYSIS` containing
all seven fields below. Every field appears; a field with no data states the
negative explicitly (e.g., `No database layer detected`) rather than being
omitted.

| Field | Content |
|-------|---------|
| **Language** | The detected language (e.g., `Python`, `Node.js`) |
| **Framework** | Framework + version, or `version unknown` (e.g., `Flask 3.1.1`) |
| **Dependencies** | Declared direct dependencies (e.g., `flask, flask-cors`) |
| **Domain** | Domain phrase + key entities (e.g., `E-commerce API — produtos, usuários, pedidos`) |
| **Architecture** | High-level structure (e.g., `Monolithic — everything in 4 files, no layer separation`) |
| **Source files** | Accurate count + the list of analyzed source files (e.g., `4 (app.py, controllers.py, models.py, database.py)`) |
| **DB tables** | Each detected table/entity by name, or `No database layer detected` |

Example shape (values must reflect the actual project):

```
PHASE 1: PROJECT ANALYSIS
Language:     Python
Framework:    Flask 3.1.1
Dependencies: flask, flask-cors
Domain:       E-commerce API — produtos, usuários, pedidos
Architecture: Monolithic — everything in 4 files, no layer separation
Source files: 4 (app.py, controllers.py, models.py, database.py)
DB tables:    produtos, usuarios, pedidos
```

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
