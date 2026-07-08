# ARCHITECTURE AUDIT REPORT

## Header
- **Project:** task-manager-api
- **Stack:** Python / Flask 3.0.0 (flask-sqlalchemy 3.1.1)
- **Domain:** Task management API — tasks, users, categories
- **Files analyzed:** 15
- **Lines analyzed:** 1158
- **Date:** 2026-07-08

## Severity Summary
CRITICAL: 2 | HIGH: 3 | MEDIUM: 4 | LOW: 2
Total findings: 11

## Findings

### [CRITICAL] AP-01 — Hardcoded Credentials / Secrets
- **File:** `app.py:11-13` (also `services/notification_service.py:7-10`)
- **Description:** `SECRET_KEY = 'super-secret-key-123'`, the SQLite URI, and `SQLALCHEMY_TRACK_MODIFICATIONS` are hardcoded directly in `app.py`. `NotificationService.__init__` hardcodes `email_user = 'taskmanager@gmail.com'` and `email_password = 'senha123'`. `python-dotenv` is declared as a dependency but never used.
- **Impact:** Secrets leak through version control; rotation requires a code change and redeploy; a repo leak is an immediate breach of the app signing key and the SMTP mailbox.
- **Recommendation:** Extract all config/secrets into a `config/` module backed by environment variables and ship a `.env.example`. See playbook **P-01 (Extract Config & Secrets)**.

### [CRITICAL] AP-03 — Missing Authentication / Authorization on Sensitive Routes
- **File:** `routes/user_routes.py:134` (also `routes/task_routes.py:225`, `routes/report_routes.py:211`)
- **Description:** No auth decorator or middleware guards any route. `DELETE /users/<id>` cascades and deletes the user plus all their tasks; `DELETE /tasks/<id>`, `DELETE /categories/<id>`, `POST /users`, and `PUT /users/<id>` are all reachable anonymously. `POST /login` (`user_routes.py:210`) returns a static `'fake-jwt-token-' + id` that grants nothing and is never verified.
- **Impact:** Any anonymous caller can read, mutate, or destroy protected data (users, tasks, categories) with no credentials.
- **Recommendation:** Introduce an auth decorator/middleware applied centrally to sensitive routes, and issue/verify real tokens. See playbook **P-08 (Centralize Auth Middleware)**.

### [HIGH] AP-05 — Business Logic in Route Handlers
- **File:** `routes/task_routes.py:85-154` (also `routes/report_routes.py:12-101`)
- **Description:** Route handlers carry all validation, orchestration, and response shaping. `create_task` performs title/status/priority validation, FK existence checks, date parsing, tag normalization, and persistence inline. `summary_report` runs a ~90-line aggregation (status/priority counts, overdue scan, 7-day activity, per-user productivity) entirely inside the view.
- **Impact:** Logic cannot be reused or unit-tested independently of Flask; views are fat and hard to reason about; the same rules drift across handlers.
- **Recommendation:** Move business logic into a `controllers/` layer, keeping routes thin (parse → call controller → return). See playbook **P-04 (Move Business Logic to Controllers)**.

### [HIGH] AP-04 — God File
- **File:** `routes/report_routes.py:1-224` (also `routes/task_routes.py:1-300`)
- **Description:** `report_routes.py` mixes two unrelated responsibilities — report aggregation *and* full Category CRUD — in one 224-line file. `task_routes.py` is 300 lines combining routing, validation, DB access, and overdue computation with no service boundary.
- **Impact:** Untestable, high-churn, high-merge-conflict; violates single responsibility; every change risks unrelated breakage.
- **Recommendation:** Split by responsibility into routes/controllers/models, and separate Category routes from Reports. See playbook **P-03 (Split God Class into MVC layers)**.

### [HIGH] AP-06 — Tight Coupling / No Dependency Injection
- **File:** `services/notification_service.py:5-10` (also models importing global `db`)
- **Description:** `NotificationService` constructs its own SMTP host/port/user/password inside `__init__` with no injection point, so it cannot be substituted or mocked. Every model (`models/task.py:1`, `models/user.py:1`, `models/category.py:1`) binds to the module-global `db` imported from `database.py`, and `seed.py` imports the fully constructed `app`.
- **Impact:** Cannot swap implementations or mock in tests; hidden global state; brittle startup ordering.
- **Recommendation:** Inject dependencies (SMTP config, db/session) through a composition root. See playbook **P-05 (Introduce Dependency Injection)**.

### [MEDIUM] AP-07 — N+1 Query
- **File:** `routes/task_routes.py:41-57` (also `routes/report_routes.py:53-68`)
- **Description:** `get_tasks` loops over every task and issues `User.query.get(...)` and `Category.query.get(...)` per iteration. `summary_report` loops over every user and issues `Task.query.filter_by(user_id=...)` per user; `get_categories` (`report_routes.py:161-164`) runs a count query per category.
- **Impact:** Database round-trips scale linearly with result size; latency and load balloon under real data.
- **Recommendation:** Batch with a join / `IN` query / eager loading (`joinedload`). See playbook **P-06 (Fix N+1 with Batched Query)**.

### [MEDIUM] AP-08 — Duplicated Logic (Copy-Paste)
- **File:** `routes/task_routes.py:30-39` (repeated at `routes/task_routes.py:71-80`, `routes/task_routes.py:283-287`, `routes/user_routes.py:171-180`, `routes/report_routes.py:33-37`)
- **Description:** The overdue-computation block (`if due_date < now and status not in {done,cancelled}`) is copy-pasted across five handlers even though `Task.is_overdue()` (`models/task.py:50`) already implements it. `get_tasks` also re-inlines the full `to_dict` serialization instead of calling `Task.to_dict()`.
- **Impact:** Fixes and rule changes must be applied in many places; drift causes inconsistent overdue reporting across endpoints.
- **Recommendation:** Extract a single shared helper / reuse `Task.is_overdue()`. See playbook **P-07 (Extract Shared Helper)**.

### [MEDIUM] AP-09 — Missing / Inconsistent Error Handling
- **File:** `routes/task_routes.py:62` (also `:137`, `:236`, `routes/user_routes.py:130`, `:149`, `routes/report_routes.py:186`, `:207`, `:222`)
- **Description:** Handlers use bare `except:` clauses that swallow all exceptions and each format their own ad-hoc `{'error': ...}` response. There is no centralized error handler, and `app.run(debug=True)` (`app.py:34`) leaks stack traces to clients on any unhandled path.
- **Impact:** Inconsistent API error responses, leaked internals, and hard-to-debug silent failures.
- **Recommendation:** Register one centralized error handler (`@app.errorhandler`) and let handlers raise. See playbook **P-09 (Centralize Error Handling)**.

### [MEDIUM] AP-11 — Deprecated API Usage
- **File:** `models/task.py:15` (widespread: `models/task.py:16,52`, `models/user.py:14`, `models/category.py:11`, `routes/task_routes.py:31,72,285`, `routes/user_routes.py:172`, `routes/report_routes.py:35,42,45,71`, `utils/helpers.py:38`, `seed.py:66`)
- **Description:** `datetime.utcnow()` is used pervasively as column defaults and in overdue math; it is deprecated from Python 3.12 in favor of timezone-aware `datetime.now(timezone.utc)`. Data access also uses the legacy `Model.query.get(...)` API deprecated in SQLAlchemy 2.0.
- **Impact:** Breaks on the next runtime/library upgrade; naive UTC timestamps invite timezone bugs; blocks maintenance.
- **Recommendation:** Replace with `datetime.now(timezone.utc)`. See playbook **P-11 (Replace Deprecated API)**.

### [LOW] AP-10 — Magic Numbers / Hardcoded Literals
- **File:** `routes/task_routes.py:110` (also `:113`, `:96-100`, `:177`, `services/notification_service.py:9`)
- **Description:** The status list `['pending','in_progress','done','cancelled']` and priority bounds `1..5` are inlined and duplicated across handlers; title length limits `3`/`200`, SMTP port `587`, and the `days=7` recent-activity window are unexplained literals. `utils/helpers.py:110-116` already defines `VALID_STATUSES`, `MAX_TITLE_LENGTH`, etc., but the routes ignore them.
- **Impact:** Intent is opaque; the same literal changed in one place but not another causes subtle inconsistencies.
- **Recommendation:** Reuse/centralize named constants and config. See playbook **P-10 (Extract Magic Numbers to Constants)**.

### [LOW] AP-12 — Poor / Misleading Naming
- **File:** `routes/report_routes.py:24-28` (also `models/category.py:14`, `utils/helpers.py:25`)
- **Description:** Non-trivial values carry single-letter or meaningless names: `p1..p5` for per-priority counts, `t`/`u`/`c`/`td` loop variables throughout the routes, `d = {...}` for the category dict in `Category.to_dict`, and `s` in `sanitize_string(s)`.
- **Impact:** Raises the cost of reading and safely changing the code.
- **Recommendation:** Rename to intention-revealing identifiers (e.g. `priority_1_count`, `task`, `user`). See playbook **P-12 (Rename for Intent)**.
