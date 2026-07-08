# ARCHITECTURE AUDIT REPORT

## Header
- **Project:** ecommerce-api-legacy
- **Stack:** Node.js / Express ^4.18.2
- **Domain:** LMS / e-commerce checkout API — users, courses, enrollments, payments, audit_logs
- **Files analyzed:** 3
- **Lines analyzed:** 180
- **Date:** 2026-07-08

## Severity Summary
CRITICAL: 2 | HIGH: 3 | MEDIUM: 3 | LOW: 2
Total findings: 10

## Findings

### [CRITICAL] AP-01 — Hardcoded Credentials / Secrets
- **File:** `src/utils.js:1-7`
- **Description:** The `config` object literally embeds `dbUser`, `dbPass` (`"senha_super_secreta_prod_123"`), `paymentGatewayKey` (`"pk_live_1234567890abcdef"`), and `smtpUser` in source. The live payment key is also logged to stdout at `src/AppManager.js:45`.
- **Impact:** Production secrets leak through version control; a repo leak is an immediate breach. Rotation requires a code change and redeploy. Logging the gateway key exposes it in log aggregators.
- **Recommendation:** Move all config into an env-backed config module and read from `process.env`; ship a `.env.example`. Playbook **P-01 (Extract Config & Secrets)**.

### [CRITICAL] AP-03 — Missing Authentication / Authorization on Sensitive Routes
- **File:** `src/AppManager.js:80` (`GET /api/admin/financial-report`), `src/AppManager.js:131` (`DELETE /api/users/:id`)
- **Description:** The admin financial report and the user-deletion endpoint have no authentication or authorization guard — any anonymous caller can read all revenue/student data or delete any user by id.
- **Impact:** Anonymous data exfiltration of financial records and destructive, unauthenticated deletion of users. Direct data exposure and integrity loss.
- **Recommendation:** Introduce an auth middleware applied centrally to sensitive routes. Playbook **P-08 (Centralize Auth Middleware)**.

### [HIGH] AP-04 — God Class / God File
- **File:** `src/AppManager.js:4-141`
- **Description:** `AppManager` owns database construction, schema creation + seeding (`initDb`), all route registration, and all business logic (checkout, reporting, deletion) in a single class.
- **Impact:** Untestable, high-churn, high-merge-conflict; violates single responsibility; every change risks unrelated breakage.
- **Recommendation:** Split by responsibility into models / controllers / routes. Playbook **P-03 (Split God Class into MVC layers)**.

### [HIGH] AP-05 — Business Logic in Route Handlers
- **File:** `src/AppManager.js:28-78`
- **Description:** The `/api/checkout` handler inlines input validation, user lookup/creation, password hashing, payment decisioning (`cc.startsWith("4")`), enrollment + payment + audit inserts, and response shaping — all inside the route callback.
- **Impact:** The checkout logic cannot be reused or unit-tested; the route layer is fat and hard to reason about; nested callbacks obscure control flow.
- **Recommendation:** Move orchestration into a controller/service; keep the route thin. Playbook **P-04 (Move Business Logic to Controllers)**.

### [HIGH] AP-06 — Tight Coupling / No Dependency Injection
- **File:** `src/AppManager.js:7`
- **Description:** `AppManager`'s constructor instantiates `new sqlite3.Database(':memory:')` directly, hardwiring the concrete driver and connection. No dependency is injected; the DB cannot be substituted or mocked.
- **Impact:** Cannot swap implementations or mock in tests; hidden global state; brittle startup ordering.
- **Recommendation:** Construct the connection in a composition root and inject a repository/db into consumers. Playbook **P-05 (Introduce Dependency Injection)**.

### [MEDIUM] AP-07 — N+1 Query
- **File:** `src/AppManager.js:83-127`
- **Description:** `financial-report` fetches all courses, then for each course queries its enrollments, then for each enrollment issues a separate query for the user and another for the payment — a query per row at every level.
- **Impact:** Database round-trips scale linearly (multiplicatively) with data size; latency and load balloon under real data. The manual pending-counter fan-out is also error-prone.
- **Recommendation:** Batch with joins / `IN` queries (or an aggregate query) instead of per-row lookups. Playbook **P-06 (Fix N+1 with Batched Query)**.

### [MEDIUM] AP-08 — Duplicated Logic (Copy-Paste)
- **File:** `src/AppManager.js:38,41,51,55` (repeated ad-hoc `res.status(500).send("Erro …")` / `res.status(404)` blocks)
- **Description:** Near-identical error-return blocks (`if (err …) return res.status(5xx).send("Erro …")`) are copy-pasted across the checkout callback chain, each with a slightly different string.
- **Impact:** Fixes and changes must be applied in many places; drift causes inconsistent error behavior and bugs.
- **Recommendation:** Extract a shared error/response helper and let errors bubble. Playbook **P-07 (Extract Shared Helper)**.

### [MEDIUM] AP-09 — Missing / Inconsistent Error Handling
- **File:** `src/AppManager.js:131-137`
- **Description:** The `DELETE /api/users/:id` handler ignores the `err` argument entirely and always returns 200 with a hardcoded message even on failure; across the app each handler formats its own ad-hoc error strings and there is no centralized error handler/middleware.
- **Impact:** Inconsistent API responses, silent failures, and no single place to format/observe errors; clients cannot rely on error semantics.
- **Recommendation:** Register a single Express error-handling middleware; handlers raise/`next(err)` rather than each formatting their own. Playbook **P-09 (Centralize Error Handling)**.

### [LOW] AP-10 — Magic Numbers / Hardcoded Literals
- **File:** `src/utils.js:18-22`, `src/AppManager.js:46`
- **Description:** `badCrypto` loops `10000` times and slices `substring(0, 2)` / `substring(0, 10)` with no named constants; the payment decision keys off the magic literal `"4"` (`cc.startsWith("4")`). Intent is opaque.
- **Impact:** The meaning of each literal is unclear; changing one occurrence but not another causes subtle bugs.
- **Recommendation:** Extract into named constants/config. Playbook **P-10 (Extract Magic Numbers to Constants)**.

### [LOW] AP-12 — Poor / Misleading Naming
- **File:** `src/AppManager.js:29-33`
- **Description:** The checkout handler binds single-letter/cryptic identifiers (`u`, `e`, `p`, `cid`, `cc`) for user, email, password, course id, and card; helper `logAndCache` also does more/less than its name implies.
- **Impact:** Raises the cost of reading and safely changing the code.
- **Recommendation:** Rename to intention-revealing identifiers (`userName`, `email`, `password`, `courseId`, `cardNumber`). Playbook **P-12 (Rename for Intent)**.
