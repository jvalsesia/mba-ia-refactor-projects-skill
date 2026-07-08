# Implementation Plan: Phase 2 — Architecture Audit & Report

**Prerequisites:**
- F01 is implemented: `.claude/skills/refactor-arch/SKILL.md` exists with a Phase 2 section stub, and `references/anti-patterns-catalog.md` and `references/report-template.md` are present and loadable
- F02 is implemented: Phase 1 produces the stack profile + architecture map (language, framework, dependencies, domain, analyzed files, DB tables) in context
- The three target projects (`code-smells-project`, `task-manager-api`, `ecommerce-api-legacy`) are available to validate audit accuracy
- No runtime libraries, database, or environment variables required — the deliverable is pure Markdown authored into `SKILL.md`

### Stage 1: Audit Detection & Classification

**1. Consume the Phase 1 profile** - In the `SKILL.md` Phase 2 section, instruct the phase to reuse the F02 stack profile + architecture map (analyzed file list, stack, domain, DB tables) as its input, without re-detecting the stack. Reference spec Section 5 Contract A.

**2. Cross-reference against the catalog** - Author the instructions that load `references/anti-patterns-catalog.md` and cross-reference the analyzed code against every catalog entry, including deprecated-API detection, using the catalog as the sole finding knowledge with no hardcoded checks. Reference spec Section 5 Contract B and Section 8.

**3. Classify and locate findings** - Specify that each finding is classified into exactly one severity (CRITICAL/HIGH/MEDIUM/LOW) and carries an exact `file:line` (or `file:start-end`), a description, an impact, and a recommendation that names a playbook pattern. Reference spec Section 6.

### Stage 2: Report Rendering & Persistence

**4. Render the report via the template** - Specify assembling the findings into the `ARCHITECTURE AUDIT REPORT` block using `references/report-template.md`: the Header, the per-severity summary (`CRITICAL: n | HIGH: n | MEDIUM: n | LOW: n`) plus total, and the finding blocks ordered CRITICAL → LOW. Reference spec Section 6.

**5. Save the report and handle edge cases** - Encode saving the rendered report to `reports/audit-project-N.md` with sequential gap-filling `N`, creating the `reports/` directory if absent; flagging the unmet threshold when fewer than 5 findings are found; and surfacing a write error without advancing when the file cannot be written. Reference spec Sections 6 and 8.

### Stage 3: Gate Hand-off & Validation

**6. Reach the confirmation gate and hand off to F04** - Ensure Phase 2 reaches the F01 confirmation gate only after the report is fully rendered and saved with no source file modified, and that the findings set plus the persisted report path are carried forward as the exact inputs F04 acts upon. Reference spec Section 5 Contract C.

**7. Behavioral and structural verification** - Confirm the Phase 2 section produces ≥5 findings with ≥1 CRITICAL/HIGH per target project, each with an exact location and full fields, ordered CRITICAL → LOW, saved via the template, modifying no source file; and confirm the persisted report matches the findings that feed F04. Reference the acceptance and integration tests in spec Section 7.
