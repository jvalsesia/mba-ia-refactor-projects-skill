# Implementation Plan: Phase 1 — Project Analysis

**Prerequisites:**
- F01 is implemented: `.claude/skills/refactor-arch/SKILL.md` exists with a Phase 1 section stub, and `references/detection-heuristics.md` is present and loadable
- The three target projects (`code-smells-project`, `task-manager-api`, `ecommerce-api-legacy`) are available to validate detection accuracy
- No runtime libraries, database, or environment variables required — the deliverable is pure Markdown authored into `SKILL.md`

### Stage 1: Phase 1 Detection Logic

**1. Load detection knowledge** - In the `SKILL.md` Phase 1 section, instruct the phase to load `references/detection-heuristics.md` and use it as the sole source of detection signals, with no hardcoded stack assumptions. Reference spec Section 5 Contract A.

**2. Apply the six detection categories** - Author the instructions that walk the current working directory and apply the heuristics' Language, Framework/version, Dependencies, Database/tables, Domain, and Architecture categories, computing an accurate analyzed-source-file count. Reference spec Section 6 and the detection categories in the F01 heuristics file.

**3. Emit the analysis summary** - Specify the fixed-format `PHASE 1: PROJECT ANALYSIS` block containing all seven fields (Language, Framework, Dependencies, Domain, Architecture, Source files, DB tables), stating negatives explicitly when a field has no data. Reference the output schema in spec Section 6.

### Stage 2: Guarantees and Hand-off

**4. Read-only guarantee and empty-source guard** - Encode that Phase 1 modifies no file, and that a directory with no analyzable source prints `No analyzable source files found` and stops before Phase 2. Reference the Error Handling behavior in spec Sections 1 and 7.

**5. Stack profile hand-off** - Ensure the printed summary and its in-context stack profile + architecture map carry every field F03 needs (language, framework, dependencies, domain, analyzed files, DB tables) forward to Phase 2. Reference spec Section 5 Contract B.

### Stage 3: Validation

**6. Behavioral and structural verification** - Confirm the Phase 1 section detects language, framework/version, DB tables, domain, and an accurate file count correctly across all three target projects, modifies no file, and correctly stops on an empty directory; confirm the profile feeds the F03 audit. Reference the acceptance and integration tests in spec Section 7.
