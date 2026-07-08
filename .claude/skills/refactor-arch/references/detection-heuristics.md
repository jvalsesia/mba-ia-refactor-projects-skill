# Detection Heuristics

Signal-based rules for identifying a project's stack and architecture. Phase 1
(Analysis) applies these. Every rule is a *signal → conclusion* pairing; prefer
concrete file/content signals over guesses. When signals conflict, report the
strongest evidence and note the ambiguity rather than assuming.

## Category 1 — Language

| Signal | Conclusion |
|--------|-----------|
| `.py` files present + `requirements.txt` / `pyproject.toml` / `Pipfile` | Python |
| `.js` / `.mjs` / `.ts` files + `package.json` | JavaScript / TypeScript (Node.js) |
| `.rb` + `Gemfile` | Ruby |
| `.go` + `go.mod` | Go |
| `.java` + `pom.xml` / `build.gradle` | Java |

Method: glob the tree for source extensions, count each, and pick the dominant
language. Record the count so Phase 1 can report an accurate analyzed-file total.

## Category 2 — Framework / version

| Signal | Conclusion |
|--------|-----------|
| `from flask import` / `Flask(__name__)` in source; `flask` in `requirements.txt` | Flask (Python) |
| `django` in `requirements.txt`; `manage.py` present | Django (Python) |
| `fastapi` in deps; `FastAPI(` in source | FastAPI (Python) |
| `require('express')` / `from 'express'`; `express` in `package.json` | Express (Node.js) |
| `@nestjs/core` in `package.json` | NestJS (Node.js) |

Version: read the pinned version from the dependency manifest
(`flask==3.0.0`, `"express": "^4.19.2"`). If a range is given, report the
range. If no version is pinned, report `version unknown`.

## Category 3 — Dependencies

- **Python:** parse `requirements.txt` (one `pkg==ver` per line),
  `pyproject.toml` `[project].dependencies`, or `Pipfile` `[packages]`.
- **Node.js:** parse `package.json` `dependencies` and `devDependencies`.
- Report the dependency list, flagging any that are known-deprecated or
  unmaintained (feeds the deprecated-API check in the catalog).

## Category 4 — Database / tables

- Scan for SQL: `CREATE TABLE <name>`, `.sql` files, migration folders.
- Scan for ORM models: SQLAlchemy `class X(db.Model)` / `__tablename__`,
  Sequelize `sequelize.define('name', …)`, Django `class X(models.Model)`.
- Scan for raw drivers: `sqlite3.connect(...)`, `psycopg2`, `mysql2`, `pg`.
- Report each detected table/entity by name (e.g., `users`, `orders`,
  `products`). If none found, report `No database layer detected`.

## Category 5 — Domain

Infer the application domain from route paths, model names, and table names,
not from filenames alone:

- Routes `/products`, `/orders`, `/cart` + tables `products`, `orders` →
  "E-commerce API".
- Routes `/tasks`, `/projects` + table `tasks` → "Task management API".
- Report as a short phrase plus the key entities, e.g.
  `E-commerce API — produtos, pedidos, usuários`.

## Category 6 — Architecture

- Count source files and inspect layer separation.
- **Monolithic / no layers:** most logic in 1–4 files, routes + DB + business
  logic mixed in the same file → `Monolithic — everything in N files, no layer
  separation`.
- **Partial layering:** some separation (a `models/` dir but fat route
  handlers) → note which layers exist and which are missing.
- **MVC / layered:** distinct `models`, `controllers`, `routes`/`views`,
  `config` directories → `Layered (MVC-like)`.
- Report the analyzed-file count here so it matches the real number of source
  files in the project.
