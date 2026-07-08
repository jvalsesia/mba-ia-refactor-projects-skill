# Audit Report Template

The standardized layout Phase 2 (Audit) renders and saves to
`reports/audit-project-N.md`. Every run produces the same shape so reports are
comparable and shareable. Fill every placeholder; do not drop blocks.

The report has three required blocks: **Header**, **Severity summary**, and one
**Finding block** per finding. Findings are ordered CRITICAL → HIGH → MEDIUM →
LOW.

---

```markdown
# ARCHITECTURE AUDIT REPORT

## Header
- **Project:** <project name / directory>
- **Stack:** <language> / <framework> <version>
- **Domain:** <inferred domain — key entities>
- **Files analyzed:** <count>
- **Lines analyzed:** <count>
- **Date:** <YYYY-MM-DD>

## Severity Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>
Total findings: <total>

<!-- If total < 5, add this line: -->
> ⚠️ Minimum finding threshold (5) not met — consider widening the catalog or re-running.

## Findings

### [CRITICAL] <Anti-pattern name>
- **File:** `<path>:<line>` (or `<path>:<start>-<end>`)
- **Description:** <what the code does that is wrong>
- **Impact:** <why it matters / the risk>
- **Recommendation:** <concrete fix, referencing a playbook pattern e.g. P-01>

### [HIGH] <Anti-pattern name>
- **File:** `<path>:<line>`
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

### [MEDIUM] <Anti-pattern name>
- **File:** `<path>:<line>`
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

### [LOW] <Anti-pattern name>
- **File:** `<path>:<line>`
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...
```

---

## Rules

- **Header** is required: project name, stack, domain, and file/line counts must
  be present.
- **Severity summary** is required and must use the exact form
  `CRITICAL: n | HIGH: n | MEDIUM: n | LOW: n` followed by a total.
- **Finding block** is required for each finding and must contain, in order:
  `[SEVERITY] Name`, **File** with an exact `path:line` (or `path:start-end`),
  **Description**, **Impact**, **Recommendation**.
- Order findings strictly CRITICAL → LOW. Within a severity, most-impactful
  first.
- The report is saved to `reports/audit-project-N.md` (N distinguishes multiple
  audited projects). The confirmation gate is presented only after this file is
  written.
