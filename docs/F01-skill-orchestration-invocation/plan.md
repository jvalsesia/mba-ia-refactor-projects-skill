# Implementation Plan: Skill Orchestration & Invocation

**Prerequisites:**
- Claude Code CLI installed and able to discover project-level skills under `.claude/skills/`
- Reference materials: the PRD severity scale and the three target projects (`code-smells-project`, `task-manager-api`, `ecommerce-api-legacy`) available to validate copyability
- No runtime libraries, database, or environment variables required — the deliverable is pure Markdown

### Stage 1: Skill Scaffold and Entry Point

**1. Skill folder structure** - Create the `.claude/skills/refactor-arch/` directory with its `references/` subfolder so the skill is discoverable by `/refactor-arch`. See spec Section 2 for the exact paths.

**2. SKILL.md orchestrator** - Author the entry-point file with valid frontmatter and the `/refactor-arch` trigger, the strict Analysis → Audit → Refactoring sequencing, and explicit instructions to load every reference file at the start of a run. Reference spec Section 4 for responsibilities and Section 5 Contract A for what must be loadable.

**3. Confirmation gate** - Define the mandatory human gate in the orchestrator: after Phase 2, present the report, stop, and await a `y/n` reply, treating anything other than `y` as an abort with zero mutations. Reference spec Section 5 Contract B for the decision semantics.

**4. Orchestration error handling** - Encode the orchestration-level failure behaviors: no analyzable source files, a missing reference file, a non-`y` gate response, and interruption between phases leaving no partial changes. Reference the Error Handling behaviors captured in spec Sections 1 and 5.

### Stage 2: Reference Knowledge Authoring

**5. Detection heuristics reference** - Write the full detection-heuristics file covering language, framework/version, dependencies, database, domain, and architecture signals for the target stacks. Reference the required categories in spec Section 6.

**6. Anti-pattern catalog reference** - Write the catalog with at least eight anti-patterns spanning all four severities and including deprecated-API detection, each entry carrying a name, severity, detection signal, impact, and recommendation. Reference the catalog schema and constraints in spec Section 6.

**7. Report template and MVC guidelines references** - Write the standardized audit report template (header, severity summary, ordered finding blocks) and the MVC guidelines defining the config, models, views/routes, controllers, error-handling, and entry-point layers. Reference the required blocks and layers in spec Section 6.

**8. Refactoring playbook reference** - Write the playbook with at least eight before/after transformation patterns, each mapped to a catalog anti-pattern. Reference the pattern schema and constraints in spec Section 6.

### Stage 3: Validation and Copyability

**9. Structural verification** - Confirm the scaffold, all six files, the catalog and playbook minimums, valid frontmatter, and the pure-Markdown constraint. Reference the structural checks in spec Section 7.

**10. Copyability and integration check** - Copy the skill folder unchanged into a second target project and confirm the pipeline still runs, and that the loaded knowledge and the gate decision flow correctly into the later phases. Reference the acceptance and integration tests in spec Section 7.
