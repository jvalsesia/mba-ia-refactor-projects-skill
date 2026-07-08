# Refactoring Playbook

Before/after transformation patterns Phase 3 (Refactoring) applies to eliminate
audited anti-patterns. Each pattern names its **Target anti-pattern** (from the
catalog), shows a **Before** (the smell) and an **After** (the MVC-conformant
fix), and optional **Notes**. Every fixable catalog anti-pattern maps to at
least one pattern here. This playbook contains **12** patterns.

---

## P-01 — Extract Config & Secrets
**Target anti-pattern:** AP-01 (Hardcoded Credentials / Secrets)

**Before**
```python
# app.py
SECRET_KEY = "hunter2"
db = connect("postgres://admin:pass@localhost/app")
```

**After**
```python
# config/settings.py
import os
SECRET_KEY = os.environ["SECRET_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

# app.py
from config.settings import SECRET_KEY, DATABASE_URL
db = connect(DATABASE_URL)
```
**Notes:** ship a `.env.example` documenting required vars; never commit `.env`.

---

## P-02 — Parameterize Queries
**Target anti-pattern:** AP-02 (SQL Injection via String Interpolation)

**Before**
```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**After**
```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```
**Notes:** Node.js — use placeholders (`db.query('… WHERE id = $1', [id])`) or
an ORM's parameter binding; never interpolate into the SQL string.

---

## P-03 — Split God Class into MVC Layers
**Target anti-pattern:** AP-04 (God Class / God File)

**Before**
```
app.py  (routes + SQL + validation + config, 500 lines)
```

**After**
```
routes/user_routes.py       # routing only
controllers/user_controller.py  # validation + orchestration
models/user.py              # data access
config/settings.py          # config
```
**Notes:** move code in small steps, keeping the app runnable between moves.

---

## P-04 — Move Business Logic to Controllers
**Target anti-pattern:** AP-05 (Business Logic in Route Handlers)

**Before**
```python
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    if data["total"] < 0: return "bad", 400
    total = sum(i["price"] for i in data["items"]) * 1.1
    cursor.execute("INSERT INTO orders ...")
    return "ok"
```

**After**
```python
# routes/order_routes.py
@app.route("/orders", methods=["POST"])
def create_order():
    return order_controller.create(request.json)

# controllers/order_controller.py
def create(data):
    validate_order(data)
    total = calculate_total(data["items"])
    return Order.insert(total)
```

---

## P-05 — Introduce Dependency Injection
**Target anti-pattern:** AP-06 (Tight Coupling / No DI)

**Before**
```python
# models/user.py
db = sqlite3.connect("app.db")   # global, created at import
def get(uid): return db.execute(...)
```

**After**
```python
# models/user.py
class UserRepository:
    def __init__(self, db): self.db = db
    def get(self, uid): return self.db.execute(...)

# app.py (composition root)
db = create_connection(config.DATABASE_URL)
user_repo = UserRepository(db)
```
**Notes:** enables mocking in tests and swapping the backing store.

---

## P-06 — Fix N+1 with Batched Query
**Target anti-pattern:** AP-07 (N+1 Query)

**Before**
```python
orders = get_orders()
for o in orders:
    o.user = get_user(o.user_id)   # one query per order
```

**After**
```python
orders = get_orders()
user_ids = [o.user_id for o in orders]
users = get_users_in(user_ids)     # single query: WHERE id IN (...)
by_id = {u.id: u for u in users}
for o in orders:
    o.user = by_id[o.user_id]
```
**Notes:** with an ORM, use eager loading (`joinedload` / `include`).

---

## P-07 — Extract Shared Helper
**Target anti-pattern:** AP-08 (Duplicated Logic)

**Before**
```python
# repeated in 3 handlers
if not request.json.get("email"): return jsonify(error="email required"), 400
```

**After**
```python
# controllers/validation.py
def require_fields(data, fields):
    missing = [f for f in fields if not data.get(f)]
    if missing: raise ValidationError(missing)

# each handler
require_fields(request.json, ["email"])
```

---

## P-08 — Centralize Auth Middleware
**Target anti-pattern:** AP-03 (Missing Authentication / Authorization)

**Before**
```python
@app.route("/admin/users")
def admin_users():          # no auth check at all
    return all_users()
```

**After**
```python
# middleware/auth.py
def require_auth(fn):
    @wraps(fn)
    def wrapper(*a, **k):
        if not valid_token(request): abort(401)
        return fn(*a, **k)
    return wrapper

# routes
@app.route("/admin/users")
@require_auth
def admin_users(): return all_users()
```

---

## P-09 — Centralize Error Handling
**Target anti-pattern:** AP-09 (Missing / Inconsistent Error Handling)

**Before**
```python
@app.route("/x")
def x():
    try: ...
    except Exception as e: return str(e), 500   # ad-hoc, leaks internals
```

**After**
```python
# middleware/error_handler.py
@app.errorhandler(Exception)
def handle(e):
    status = getattr(e, "status", 500)
    return jsonify(error=e.public_message()), status
# handlers just raise; the central handler formats every error consistently
```
**Notes:** Node/Express — a single `app.use((err, req, res, next) => …)` at the
end of the middleware chain.

---

## P-10 — Extract Magic Numbers to Constants
**Target anti-pattern:** AP-10 (Magic Numbers / Hardcoded Literals)

**Before**
```python
if user.role == 2: ...
token_ttl = 3600
```

**After**
```python
# constants.py / config
class Role: ADMIN = 2
TOKEN_TTL_SECONDS = 3600

if user.role == Role.ADMIN: ...
token_ttl = TOKEN_TTL_SECONDS
```

---

## P-11 — Replace Deprecated API
**Target anti-pattern:** AP-11 (Deprecated API Usage)

**Before**
```python
from datetime import datetime
now = datetime.utcnow()            # deprecated in 3.12+
```
```js
const buf = new Buffer(len);       // deprecated
```

**After**
```python
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
```
```js
const buf = Buffer.alloc(len);
```
**Notes:** confirm the replacement against the detected framework/runtime
version before applying.

---

## P-12 — Rename for Intent
**Target anti-pattern:** AP-12 (Poor / Misleading Naming)

**Before**
```python
def f1(d):
    return d["p"] * d["q"]
```

**After**
```python
def calculate_line_total(item):
    return item["price"] * item["quantity"]
```
**Notes:** rename via the editor/LSP so all references update together.

---

**Coverage map:** P-01→AP-01 · P-02→AP-02 · P-03→AP-04 · P-04→AP-05 ·
P-05→AP-06 · P-06→AP-07 · P-07→AP-08 · P-08→AP-03 · P-09→AP-09 · P-10→AP-10 ·
P-11→AP-11 · P-12→AP-12. Every fixable catalog anti-pattern maps to ≥1 pattern.
