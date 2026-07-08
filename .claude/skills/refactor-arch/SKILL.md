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

### 1.4 — Read-only guarantee

Phase 1 **modifies no file**. It only reads and globs the project tree to gather
detection signals and print the summary. Do not create, edit, delete, move, or
write any file — including no scratch files, no `reports/` directory, and no
intermediate `analysis.json`. Any writing of the project's source or of new
files is a Phase 1 contract violation. The stack profile and architecture map
are carried **in conversation context**, not persisted to disk.

### 1.5 — Empty-source guard

If, after applying the Language and Architecture heuristics, the current working
directory contains **no analyzable source files** (an empty tree, or only
docs / config / vendor directories with no detected-language source), print
exactly:

```
No analyzable source files found
```

and **stop before Phase 2**. Do not proceed to the Audit phase, do not print a
`PHASE 1: PROJECT ANALYSIS` block, and modify no file. This is the guard that
prevents any downstream phase from running against an empty or unrecognized
directory.

### 1.6 — Stack profile + architecture map hand-off (to Phase 2 / F03)

The printed summary is also the in-context hand-off consumed by Phase 2. Carry
every field forward so the F03 audit reasons over it **without re-detecting**:

| Field | Part of | Guaranteed to contain |
|-------|---------|-----------------------|
| Language | Stack profile | The detected language |
| Framework + version | Stack profile | Framework and version, or `version unknown` |
| Dependencies | Stack profile | Declared direct dependencies from the manifest |
| Domain | Stack profile | Short domain phrase + key entities |
| Architecture | Architecture map | High-level structure description |
| Source files analyzed | Architecture map | Accurate count + the file list scanned |
| Database tables/entities | Architecture map | Each detected table/entity, or `No database layer detected` |

Every field above is present in the printed summary and available in context for
Phase 2. No source file is written while producing this contract.

---

## Phase 2 — Audit

Phase 2 cross-references the analyzed project against the anti-pattern catalog,
produces an ordered, severity-classified list of **findings** (each with an
exact `file:line`, description, impact, and recommendation), renders them with
`references/report-template.md`, **saves** the report to
`reports/audit-project-N.md`, and only then reaches the confirmation gate. All
audit knowledge comes from `references/anti-patterns-catalog.md` and
`references/report-template.md` (loaded in Step 0) — **never** from hardcoded,
per-project findings. Phase 2 modifies **no source file**; its only write is the
report artifact under `reports/`.

### 2.1 — Consume the Phase 1 profile (no re-detection)

Reuse the **stack profile + architecture map** that Phase 1 produced and carried
in context: language, framework + version, dependencies, domain, the analyzed
source-file list + count, and the detected database tables. Do **not** re-detect
the stack — Phase 1 already did. This profile is the input the audit reasons
over, and its analyzed-file list is the source of truth for the `file:line`
locations below and the report header's file/line counts.

### 2.2 — Cross-reference against the anti-pattern catalog

Load `references/anti-patterns-catalog.md` and use it as the **sole** source of
findings. Walk the analyzed source files and, for each catalog entry, apply its
*detection signal* to the code:

- Match every catalog anti-pattern that applies (AP-01 … AP-12), including
  **deprecated-API detection (AP-11)** when the detected stack uses a deprecated
  API (e.g., Flask `@app.before_first_request` / `datetime.utcnow()`; Node.js
  `new Buffer()` / `url.parse()` / an end-of-life pinned major).
- Report only anti-patterns defined in the catalog — do not invent ad-hoc
  findings or bake per-project results into this phase.
- Aim for **at least 5 findings** per project, with **at least 1 CRITICAL or
  HIGH**. Prefer concrete signals over speculation; a finding must point at real
  code.

### 2.3 — Classify and locate each finding

For every match, produce a finding with all of:

- **Severity** — exactly one of `CRITICAL` / `HIGH` / `MEDIUM` / `LOW`, taken
  from the catalog entry (security/architecture failures → CRITICAL; MVC/SOLID
  violations → HIGH; standardization/duplication/moderate performance/deprecated
  API → MEDIUM; readability/naming/magic numbers → LOW).
- **Location** — an exact `file:line`, or `file:start-end` for a range, resolved
  against the Phase 1 analyzed-file list.
- **Description** — what the code does that is wrong.
- **Impact** — why it matters / the risk it carries.
- **Recommendation** — the concrete fix, naming the playbook pattern the catalog
  entry references (e.g., `P-01`, `P-03`).

Order the full set strictly **CRITICAL → HIGH → MEDIUM → LOW**; within a
severity, most-impactful first.

### 2.4 — Render the report via the template

Assemble the findings into an `ARCHITECTURE AUDIT REPORT` using
`references/report-template.md`. Fill every required block; drop none:

- **Header** — `Project` (the audited directory), `Stack` (`<language> /
  <framework> <version>`), `Domain` (from the Phase 1 profile), `Files analyzed`
  and `Lines analyzed` (counted over the Phase 1 analyzed-file list), and `Date`.
- **Severity Summary** — the exact line
  `CRITICAL: n | HIGH: n | MEDIUM: n | LOW: n`, followed by
  `Total findings: <total>`.
- **Finding blocks** — one per finding, ordered CRITICAL → LOW, each as
  `### [SEVERITY] <Anti-pattern name>` with **File** (`path:line`),
  **Description**, **Impact**, and **Recommendation**.

Print this report block to the user and use the same rendered content as the
file written in 2.5.

### 2.5 — Save the report and handle edge cases

- **Save location.** Write the rendered report to `reports/audit-project-N.md`.
  If the `reports/` directory does not exist, **create it first** rather than
  failing.
- **Numbering `N`.** Choose `N` by **sequential gap-filling**: scan `reports/`
  for existing `audit-project-<k>.md` files and pick the lowest positive integer
  not yet used (first run → `audit-project-1.md`, next distinct run →
  `audit-project-2.md`), so earlier reports are preserved.
- **Below-threshold flag.** If the total is fewer than 5 findings, still render
  and save the report, but include the template's warning line noting the
  minimum finding threshold (5) was not met, so the operator can widen the
  catalog or re-run.
- **Write failure.** If the report file cannot be written, surface the write
  error to the user and **do not advance to the confirmation gate** — the
  reviewer must have a saved report to review. Writing the report is the **only**
  file write Phase 2 performs; no source file is modified.

### 2.6 — Reach the gate and hand off to Phase 3 (F04)

Once — and only once — the report has been fully rendered **and** saved to
`reports/audit-project-N.md`, Phase 2 is complete. Yield to the
**Confirmation Gate** section below (owned by the orchestrator): Phase 2 does not
implement its own prompt or decision capture. No source file has been modified at
this point, so the gate can still abort with zero mutations.

Carry forward, in context, the exact hand-off Phase 3 (F04) consumes — the same
set reflected in the saved report:

| Field | Part of | Guaranteed to contain |
|-------|---------|-----------------------|
| Anti-pattern name | Each finding | The catalog entry the code matched |
| Severity | Each finding | Exactly one of CRITICAL / HIGH / MEDIUM / LOW |
| Location | Each finding | An exact `file:line` or `file:start-end` |
| Recommendation | Each finding | The fix, naming the playbook pattern (e.g., `P-01`) |
| Report path | Persisted artifact | `reports/audit-project-N.md`, saved before the gate |

The findings F04 eliminates are exactly this set, and the persisted report
reflects the same findings F04 acts upon.

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

Phase 3 restructures the audited project **in place** into the six MVC layers
and eliminates each audited anti-pattern, then **validates** the result by
booting the app and re-running its original endpoints against a pre-refactor
baseline. It is the only phase that mutates source, so every change is driven by
an F03 finding plus a named `refactoring-playbook.md` pattern — never a free-form
rewrite. All refactoring knowledge comes from `references/mvc-guidelines.md` and
`references/refactoring-playbook.md` (loaded in Step 0); no stack-specific rule is
baked into this phase. Phase 3 prints a `PHASE 3: REFACTORING COMPLETE` summary
and reports success **only** when the boot check **and** every endpoint check
pass.

### 3.0 — Gate guard (run only on `proceed`)

Phase 3 executes **only** when the Confirmation Gate above returned `proceed`.

- If the gate decision was `abort` (any input other than exactly `y`), Phase 3
  **never runs**: leave the project **byte-for-byte unmodified** and exit. Do not
  create directories, move files, or write any source — the project must be
  indistinguishable from its pre-run state.
- Only after confirming the decision is `proceed` may you perform the first file
  mutation of the entire pipeline. Up to this point (Phases 1–2 + gate) no source
  file has been touched; that invariant is what this guard preserves. (Reference
  spec Section 5, Contract A.)

### 3.1 — Consume the inputs (findings + guidelines + playbook)

Phase 3 reasons over exactly three inputs already in context — it re-detects
nothing and invents nothing:

1. **F03 audit findings — the exact fix set.** Take the ordered findings Phase 2
   handed off (anti-pattern name, severity, `file:line`/`file:start-end`,
   recommendation) as the **complete and only** set of issues to eliminate. Do
   not add architectural changes that do not trace to a finding, and do not skip a
   finding that can be safely transformed. The set F04 eliminates is precisely the
   set F03 reported. (Reference spec Section 5, Contract C.)
2. **The persisted report — `reports/audit-project-N.md`.** Treat the saved report
   as the authoritative record of that fix set; the transformations Phase 3
   applies must correspond to the findings this report contains, so the report and
   the refactor stay in agreement.
3. **The refactoring knowledge — `mvc-guidelines.md` + `refactoring-playbook.md`.**
   Use `references/mvc-guidelines.md` as the **sole** definition of the target
   architecture (the six layers + conformance checklist) and
   `references/refactoring-playbook.md` as the **sole** catalog of transformation
   patterns (P-01 … P-12). Every change Phase 3 makes must map to a layer
   definition and/or a named playbook pattern. Do **not** hardcode a per-project
   or per-stack refactor — the same guidelines and playbook drive Flask and
   Express identically. (Reference spec Section 5, Contract B.)

### 3.2 — Capture the pre-refactor endpoint baseline

**Before mutating any file**, record how the app behaves today, so behavior can
be proven preserved afterward:

1. Boot the application in its **current** (pre-refactor) form using its existing
   entry point (e.g., `python app.py` / `flask run` / `npm start` / `node
   src/index.js`), reading the real start command from the manifest or README.
2. Enumerate the original endpoints from the current routes (method + path). Use
   the audited route definitions as the source of truth for what exists.
3. Send a representative request to each endpoint and **record its response** —
   HTTP status and body shape (and, where relevant, key fields). This recorded
   set is the **baseline**. Keep it in context; it is the comparison target in
   3.5.
4. Stop the pre-refactor app. If it cannot be booted at all in this environment
   (missing runtime, uninstallable deps, required external service absent), record
   that the baseline could not be captured and treat the endpoint check in 3.5 as
   **unverified** rather than passed — never claim endpoints match a baseline that
   was never taken.

The baseline capture reads and runs the app but is itself part of the refactor
step that the gate already authorized; it writes no source changes.

### 3.3 — Restructure in place into the six MVC layers

Using `references/mvc-guidelines.md` as the target, restructure the project **in
place** on the working tree into the six layers, adapting the directory/file
names to the detected stack while preserving each layer's responsibility:

1. **Config** — create a config module and **extract all configuration and
   credentials out of source into it**, read from environment variables (apply
   playbook **P-01**). No literal secret, DB URL, port, or environment-specific
   value may remain hardcoded anywhere else. Ship a **`.env.example`** documenting
   every required variable; do **not** create or commit a real `.env`.
2. **Models** — move all data access (schema, persistence, queries) into a models
   layer, one concern per domain entity. No raw SQL or ORM calls remain in routes
   or controllers.
3. **Views / Routes** — reduce route handlers to thin routing: parse the request,
   call a controller, return its result. No business logic or DB access in a
   route.
4. **Controllers** — move business logic / orchestration (validation, coordinating
   models, business rules, response shaping) into controllers, decoupled from the
   web framework.
5. **Centralized error handling** — register a single error-handling
   middleware/handler that formats every error consistently and never leaks stack
   traces to clients; handlers raise/bubble rather than each formatting their own
   errors.
6. **Entry point / composition root** — establish one clear entry point that loads
   config, constructs dependencies, injects them downward, registers routes and
   the error handler, and starts the server. Modules must not self-instantiate
   global connections at import time.

Move code in **small steps**, keeping the app runnable between moves (playbook
P-03). Match the illustrative target tree in `mvc-guidelines.md` (`config/`,
`models/`, `routes/` or `views/`, `controllers/`, `middleware/`, and an entry
point such as `app.py` / `index.js`), adapted to the stack.

### 3.4 — Apply one playbook pattern per audited finding

Walk the F03 findings (the fix set from 3.1) and eliminate each one with the
**named `refactoring-playbook.md` pattern its catalog entry maps to** — the fix
is chosen from the playbook, never improvised:

- Map each finding's anti-pattern to its pattern via the playbook's coverage map,
  e.g. `AP-01 → P-01` (extract config/secrets), `AP-04 → P-03` (split God
  File/Class into MVC layers), `AP-05 → P-04` (business logic → controllers),
  `AP-06 → P-05` (dependency injection), `AP-07 → P-06` (fix N+1),
  `AP-03 → P-08` (centralize auth middleware), `AP-09 → P-09` (centralize error
  handling), `AP-10 → P-10` (magic numbers → constants), `AP-11 → P-11` (replace
  deprecated API), `AP-12 → P-12` (rename for intent), etc. Apply the pattern's
  **After** shape to the audited `file:line`.
- Every audited anti-pattern must be **addressed via a playbook pattern** — the
  transformation is the concrete, principled fix for that finding, not an ad-hoc
  edit.
- **Unsafe transformations are left unresolved.** If a finding cannot be safely
  transformed (ambiguous behavior, the change would alter semantics, the pattern
  does not cleanly apply), **leave that code unchanged** and record the finding as
  **unresolved** for the summary. Never apply a partial or best-effort change that
  risks breaking the app — an honest unresolved finding beats a broken edit.

Keep a running map of `finding → pattern applied` (or `→ unresolved`) — it is
printed in the 3.6 summary and is the evidence that each audited anti-pattern was
addressed.

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
