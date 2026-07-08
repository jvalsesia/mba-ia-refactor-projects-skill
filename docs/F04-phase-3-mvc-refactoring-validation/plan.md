# Implementation Plan: Phase 3 — MVC Refactoring & Validation

**Prerequisites:**
- F01 is implemented: `.claude/skills/refactor-arch/SKILL.md` exists with a Phase 3 section stub and the confirmation gate, and `references/mvc-guidelines.md` and `references/refactoring-playbook.md` are present and loadable
- F03 is implemented: Phase 2 produces the audit findings (anti-pattern, severity, `file:line`, recommendation) in context and persists `reports/audit-project-N.md`
- The three target projects (`code-smells-project`, `task-manager-api`, `ecommerce-api-legacy`) are available to validate refactoring accuracy, each with a runnable entry point
- No new runtime libraries or environment variables are introduced by the deliverable itself — it is pure Markdown authored into `SKILL.md`

### Stage 1: Gate & Inputs

**1. Gate on the confirmation decision** - In the `SKILL.md` Phase 3 section, instruct the phase to execute only when the F01 confirmation gate returned `proceed`, and to leave the project byte-for-byte unmodified when the decision was `abort`. Reference spec Section 5 Contract A.

**2. Consume findings, guidelines, and playbook** - Author the instructions that read the F03 audit findings and persisted report as the exact set of issues to eliminate, and load `references/mvc-guidelines.md` and `references/refactoring-playbook.md` as the sole refactoring knowledge with no hardcoded stack assumptions. Reference spec Section 5 Contracts B and C.

### Stage 2: Restructure & Transform

**3. Capture the pre-refactor baseline** - Specify booting the app and recording each original endpoint's response before any change is made, so behavior can be compared after the refactor. Reference spec Section 7 (`test_endpoints_respond`) and Section 8.

**4. Restructure into the MVC layers** - Encode restructuring the project in place into the six MVC layers (config, models, views/routes, controllers, centralized error handling, entry point) per the guidelines, extracting configuration and credentials into a config module. Reference spec Section 4 and Section 5 Contract B.

**5. Apply a playbook pattern per finding** - Specify applying one refactoring-playbook transformation to eliminate each audited anti-pattern, and reporting any finding that cannot be safely transformed as unresolved rather than applying a partial change. Reference spec Sections 5, 6, and 8.

### Stage 3: Validation & Reporting

**6. Boot and endpoint validation** - Encode booting the refactored app to confirm it starts without errors, then re-running the original endpoints and comparing them to the captured baseline, reporting a boot error or a regressed endpoint when either check fails. Reference spec Section 2 and Section 7.

**7. Emit the completion summary** - Specify printing the `PHASE 3: REFACTORING COMPLETE` block with the new MVC structure, the transformations applied per finding, and the validation checklist, declaring success only when the boot and endpoint checks both pass. Reference the output schema in spec Section 6.

### Stage 4: Verification

**8. Behavioral and structural verification** - Confirm the Phase 3 section runs only on `proceed`, produces an MVC structure with no hardcoded secrets, addresses each audited anti-pattern via a playbook pattern, boots each target app, preserves original endpoint behavior against the baseline, and never reports success unless both checks pass; confirm the findings from F03 are the exact fix set. Reference the acceptance and integration tests in spec Section 7.
