# ARCHITECTURE AUDIT REPORT

## Header
- **Project:** code-smells-project
- **Stack:** Python / Flask 3.1.1
- **Domain:** E-commerce API (Loja) — produtos, usuários, pedidos, itens_pedido
- **Files analyzed:** 4 (app.py, controllers.py, models.py, database.py)
- **Lines analyzed:** 780
- **Date:** 2026-07-08

## Severity Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 2
Total findings: 11

## Findings

### [CRITICAL] AP-02 — SQL Injection via String Interpolation
- **File:** `models.py:28`, `models.py:48-49`, `models.py:58-60`, `models.py:68`, `models.py:92`, `models.py:110-111`, `models.py:127-128`, `models.py:140`, `models.py:149-166`, `models.py:174`, `models.py:280`, `models.py:289-297`; `app.py:59-78`
- **Description:** Nearly every query is built by concatenating request values straight into the SQL string (e.g. `"... WHERE id = " + str(id)`, `"... WHERE email = '" + email + "'"`, and the `buscar_produtos` `LIKE '%" + termo + "%'"`). The `/admin/query` route runs a caller-supplied SQL string verbatim.
- **Impact:** Attacker-controlled input reaches the database unescaped — enabling data theft, tampering, authentication bypass via the `login_usuario` query, and full deletion. The `/admin/query` endpoint is a remote arbitrary-SQL primitive.
- **Recommendation:** Replace every interpolated query with parameterized statements (`cursor.execute("... WHERE id = ?", (id,))`) and remove/guard `/admin/query`. See playbook **P-02 (Parameterize Queries)**.

### [CRITICAL] AP-01 — Hardcoded Credentials / Secrets
- **File:** `app.py:7`, `controllers.py:289`
- **Description:** `SECRET_KEY = "minha-chave-super-secreta-123"` is hardcoded in source, and the `/health` handler echoes the same secret key (plus `debug`, `db_path`, `ambiente`) back in its JSON response.
- **Impact:** The signing secret leaks through version control and, worse, is served to any anonymous caller of `/health` — an immediate breach requiring a code change + redeploy to rotate.
- **Recommendation:** Move the secret and all environment-specific values into an env-backed config module and stop returning them from `/health`. See playbook **P-01 (Extract Config & Secrets)**.

### [CRITICAL] AP-03 — Missing Authentication / Authorization on Sensitive Routes
- **File:** `app.py:47-57` (`/admin/reset-db`), `app.py:59-78` (`/admin/query`), `app.py:18` + `controllers.py:128-134` (`/usuarios`)
- **Description:** Destructive admin routes (`/admin/reset-db` wipes all tables; `/admin/query` runs arbitrary SQL) have no auth guard, and `GET /usuarios` returns every user record including the plaintext `senha` field.
- **Impact:** Any anonymous caller can destroy the entire dataset, run arbitrary SQL, and harvest all user passwords.
- **Recommendation:** Introduce a central auth decorator/middleware applied to sensitive routes and stop serializing the `senha` field. See playbook **P-08 (Centralize Auth Middleware)**.

### [HIGH] AP-04 — God File / No Layer Separation
- **File:** `controllers.py:1-292`, `models.py:1-314`, `app.py:1-88`
- **Description:** `controllers.py` mixes request parsing, validation, business rules, side-effects (email/SMS/push prints) and response shaping; `models.py` holds all raw SQL for four entities in one flat file; `app.py` additionally contains DB-touching route handlers. No config/models/routes/controllers/middleware separation exists.
- **Impact:** Untestable, high-churn, high-merge-conflict code; every change risks unrelated breakage and no unit boundaries exist.
- **Recommendation:** Split by responsibility into config/models/routes/controllers/middleware layers. See playbook **P-03 (Split God Class into MVC Layers)**.

### [HIGH] AP-05 — Business Logic & DB Access in Route Handlers
- **File:** `app.py:47-57`, `app.py:59-78`, `controllers.py:264-292` (`health_check`)
- **Description:** Route handlers in `app.py` open cursors and run SQL directly (`reset_database`, `executar_query`), and `health_check` issues five raw count queries inside the handler instead of delegating to a model/controller.
- **Impact:** Logic can't be reused or unit-tested; the web layer is coupled to the database and the framework, making the app hard to reason about.
- **Recommendation:** Reduce handlers to thin routing and move orchestration/queries into controllers and models. See playbook **P-04 (Move Business Logic to Controllers)**.

### [HIGH] AP-06 — Tight Coupling / No Dependency Injection
- **File:** `database.py:4-10`, and every `get_db()` call site in `models.py` / `controllers.py`
- **Description:** A single global `db_connection` is lazily created inside `get_db()` at import-reachable module scope, and every model/controller function reaches out to that global directly instead of receiving a connection.
- **Impact:** The backing store cannot be swapped or mocked in tests; hidden global state and brittle startup ordering (`check_same_thread=False` shares one connection across threads).
- **Recommendation:** Construct the connection at a composition root and inject it into repositories. See playbook **P-05 (Introduce Dependency Injection)**.

### [MEDIUM] AP-07 — N+1 Query
- **File:** `models.py:171-201` (`get_pedidos_usuario`), `models.py:203-233` (`get_todos_pedidos`), `models.py:133-166` (`criar_pedido`)
- **Description:** For each order, a query fetches its items, and then for each item another query fetches the product name — one query per item per order. `criar_pedido` similarly re-queries each product twice inside its loops.
- **Impact:** Database round-trips scale linearly with orders × items; latency and load balloon under real data volume.
- **Recommendation:** Batch with joins / `IN` queries so items and product names load in a fixed number of queries. See playbook **P-06 (Fix N+1 with Batched Query)**.

### [MEDIUM] AP-08 — Duplicated Logic (Copy-Paste)
- **File:** `controllers.py:28-50` vs `controllers.py:72-90`; `models.py:177-200` vs `models.py:209-232`
- **Description:** The product create/update validation block (required-field checks + negative price/stock checks) is duplicated across `criar_produto` and `atualizar_produto`, and the order-with-items assembly loop is copy-pasted between `get_pedidos_usuario` and `get_todos_pedidos`.
- **Impact:** Fixes must be applied in multiple places; drift produces inconsistent validation and behavior.
- **Recommendation:** Extract shared validation and order-serialization helpers. See playbook **P-07 (Extract Shared Helper)**.

### [MEDIUM] AP-09 — Missing / Inconsistent Error Handling
- **File:** `controllers.py` (every handler, e.g. `:10-12`, `:60-62`, `:95-96`, `:291-292`); `app.py:77-78`
- **Description:** Each handler wraps its body in its own `try/except Exception` and returns `str(e)` with an ad-hoc shape, leaking raw exception text (including SQL errors) to clients. There is no single error handler.
- **Impact:** Inconsistent error responses, leaked internals, and duplicated boilerplate that is easy to get wrong.
- **Recommendation:** Register one centralized `@app.errorhandler` that formats every error safely; let handlers raise. See playbook **P-09 (Centralize Error Handling)**.

### [LOW] AP-10 — Magic Numbers / Hardcoded Literals
- **File:** `models.py:257-262`, `controllers.py:47-50`, `controllers.py:52`
- **Description:** The sales-report discount tiers (`10000`/`5000`/`1000` thresholds and `0.1`/`0.05`/`0.02` rates) and the name-length bounds (`2`, `200`) plus the inline `categorias_validas` list are unexplained literals embedded in logic.
- **Impact:** Intent is opaque and the same literal changed in one place but not another causes subtle bugs.
- **Recommendation:** Extract into named constants / config. See playbook **P-10 (Extract Magic Numbers to Constants)**.

### [LOW] AP-12 — Poor / Misleading Naming
- **File:** `models.py:187-193`, `models.py:219-225`; `id` parameter shadowing across `models.py`/`controllers.py`
- **Description:** Nested cursors are named `cursor2` / `cursor3` (meaningless sequence names) and the built-in `id` is shadowed as a parameter name throughout the product functions.
- **Impact:** Raises the cost of reading and safely changing the code, and shadowing `id` masks a Python builtin.
- **Recommendation:** Rename to intention-revealing identifiers (e.g. `item_cursor`, `product_cursor`, `produto_id`). See playbook **P-12 (Rename for Intent)**.
