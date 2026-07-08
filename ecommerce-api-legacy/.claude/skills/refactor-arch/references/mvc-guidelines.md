# MVC Architecture Guidelines

The target structure Phase 3 (Refactoring) restructures a project into. MVC
here means a clean separation of responsibilities across six layers. These
definitions are stack-agnostic; the file/dir names below are conventions, adapt
them to the detected language while preserving the responsibilities.

## The six required layers

### 1. Config
- **Definition:** all externalized configuration and secrets — DB URLs, API
  keys, ports, feature flags — read from environment variables (or a `.env`
  loaded at startup), never hardcoded in source.
- **Rule:** no literal credential or environment-specific value appears outside
  the config module. Everything else imports config from here.
- **Typical location:** `config/` (Python) / `config/index.js` (Node).

### 2. Models
- **Definition:** data abstraction, one concern per domain entity — schema,
  persistence, and queries for `users`, `orders`, `products`, etc.
- **Rule:** models own all data access. No raw SQL or ORM calls leak into
  routes or controllers.
- **Typical location:** `models/`.

### 3. Views / Routes
- **Definition:** routing only — map an HTTP method + path to a controller
  function. No business logic, no DB access.
- **Rule:** a route handler is thin: parse the request, call a controller,
  return its result. If a handler contains calculations or queries, that logic
  belongs in a controller or model.
- **Typical location:** `routes/` or `views/`.

### 4. Controllers
- **Definition:** application flow / orchestration — validate input, coordinate
  models, apply business rules, shape the response.
- **Rule:** business logic lives here, not in routes and not in models. A
  controller is testable in isolation from the web framework.
- **Typical location:** `controllers/`.

### 5. Centralized Error Handling
- **Definition:** a single error-handling middleware / handler that catches
  exceptions and produces consistent, safe error responses.
- **Rule:** handlers do not each format their own errors and never leak stack
  traces to clients. Errors bubble to the central handler.
- **Typical location:** `middleware/error_handler` (Node) /
  registered error handlers / `@app.errorhandler` (Flask).

### 6. Entry Point / Composition Root
- **Definition:** one clear place that wires the app together — loads config,
  constructs dependencies, registers routes and the error handler, and starts
  the server.
- **Rule:** dependencies are constructed here and injected downward; modules do
  not self-instantiate global connections at import time.
- **Typical location:** `app.py` / `index.js` / `server.js` / `main`.

## Target directory shape (illustrative)

```
project/
├── config/            # layer 1 — env-backed config & secrets
├── models/            # layer 2 — data abstraction per entity
├── routes/  (views/)  # layer 3 — routing only
├── controllers/       # layer 4 — business logic / orchestration
├── middleware/        # layer 5 — centralized error handling, auth
└── app.py | index.js  # layer 6 — composition root / entry point
```

## Conformance checklist (used by Phase 3 validation)

- [ ] Config externalized; **no** hardcoded secrets remain in source.
- [ ] Each domain entity has a model owning its data access.
- [ ] Routes contain no business logic or direct DB access.
- [ ] Controllers hold the business logic and are framework-decoupled.
- [ ] A single centralized error handler is registered.
- [ ] One entry point wires config, dependencies, routes, and error handling.
