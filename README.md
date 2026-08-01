# Backend — FastAPI CRUD API

This guide walks you through the backend from **local run** → **production readiness** → **tests** → **CI** → **deploy on Render**.

Do one step at a time. When you want help, say which step (for example: “do Step 2”).

---

## What this backend is

| Piece | Detail |
|--------|--------|
| Framework | FastAPI |
| Package manager | Poetry |
| Database | PostgreSQL + SQLAlchemy |
| API prefix | `/api/v1` |
| Main resource | Users CRUD at `/api/v1/users/` |

### Folder layout

```
backend/
├── app/
│   ├── main.py                 # FastAPI app, CORS, lifespan
│   ├── core/config.py          # Settings from environment
│   ├── db/
│   │   ├── session.py          # Engine + DB session
│   │   ├── base.py             # SQLAlchemy Base
│   │   └── init_db.py          # Create DB / tables on startup
│   ├── models/user.py          # User table
│   ├── schemas/user.py         # Pydantic request/response models
│   └── api/v1/
│       ├── router.py
│       └── endpoints/users.py  # CRUD routes
├── .env                        # Local secrets (do not commit)
├── .env.sample                 # Example env vars (safe to commit)
├── pyproject.toml              # Dependencies
└── poetry.lock
```

### API endpoints

| Method | Path | Action |
|--------|------|--------|
| `POST` | `/api/v1/users/` | Create user |
| `GET` | `/api/v1/users/` | List users |
| `GET` | `/api/v1/users/{id}` | Get one user |
| `PUT` | `/api/v1/users/{id}` | Update user |
| `DELETE` | `/api/v1/users/{id}` | Delete user |

Interactive docs (when server is running): [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Progress checklist

- [ ] **Step 1** — Run locally
- [x] **Step 2** — Production readiness (CORS + DB init)
- [x] **Step 3** — Git + GitHub
- [x] **Step 4** — Tests
- [ ] **Step 5** — Continuous Integration (GitHub Actions)
- [ ] **Step 6** — Deploy backend on Render (CD)

---

## Step 1 — Run locally

**Goal:** API runs on your machine and talks to local PostgreSQL.

### 1.1 Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- PostgreSQL running locally

### 1.2 Install dependencies

From the `backend/` folder:

```bash
poetry install
```

### 1.3 Environment file

Copy the sample and edit values to match your Postgres user/password/database:

```bash
copy .env.sample .env
```

`.env` should look like:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/crud_db
```

### 1.4 Start the server

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

On startup, `init_db()` runs: it tries to create the database if missing, then creates tables.

### 1.5 Verify

1. Open [http://localhost:8000/docs](http://localhost:8000/docs)
2. Try `POST /api/v1/users/` then `GET /api/v1/users/`

**Done when:** CRUD works against your local Postgres.

---

## Step 2 — Production readiness

**Goal:** The app can run on a cloud host (Render) without crashing, and CORS can allow your deployed frontend later.

Today two things will break on Render if left as-is.

### 2.1 Problem: CORS is hardcoded

In `app/main.py`, origins are fixed to local Vite:

```python
allow_origins=["http://localhost:5173"],
```

On Render, the frontend will be something like `https://your-app.onrender.com`. The browser will block API calls unless that origin is allowed.

**What to do:**

1. Add `CORS_ORIGINS` to settings in `app/core/config.py` (read from env, comma-separated list).
2. Use that list in `app/main.py` instead of a hardcoded localhost URL.
3. Keep `http://localhost:5173` as the default for local development.
4. Document `CORS_ORIGINS` in `.env.sample`.

Example env (local):

```env
CORS_ORIGINS=http://localhost:5173
```

Example env (production, after frontend is deployed):

```env
CORS_ORIGINS=https://your-frontend.onrender.com
```

### 2.2 Problem: `CREATE DATABASE` on managed Postgres

In `app/db/init_db.py`, `ensure_database_exists()` connects to an admin DB and runs `CREATE DATABASE`.

On Render, the Postgres database **already exists**, and your user usually **cannot** create databases. That call will fail and the app may not start.

**What to do:**

1. Keep `create_tables()` (`Base.metadata.create_all`) for now.
2. Skip `ensure_database_exists()` in production, **or** catch the error and continue when create-database is not allowed.
3. Locally you can still auto-create the DB if you want that convenience.

### 2.3 Production start command (no reload)

Local (dev):

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

Production (Render will set `$PORT`):

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- `--host 0.0.0.0` — accept traffic from outside the container
- `$PORT` — port Render assigns
- No `--reload` — that is only for local development

**Done when:** CORS comes from env, DB init does not require `CREATE DATABASE` on managed Postgres, and you know the production start command.

---

## Step 3 — Git + GitHub

**Goal:** Put **this backend only** on GitHub as its own repo (not a monorepo with the frontend).

The git repo lives inside the `backend/` folder. The frontend will get a separate repo later.

### 3.1 Why this step matters

| Without GitHub | With GitHub |
|----------------|-------------|
| No GitHub Actions CI | Push/PR can run tests automatically |
| Manual-only deploys | Render can auto-deploy on every push to `main` |

### 3.2 What to do

1. Add a `.gitignore` in `backend/` so secrets and junk are never committed (`.env`, `.venv/`, `__pycache__/`, etc.).
2. `git init` **inside** `backend/` (this folder is the repo root).
3. Commit your backend code.
4. Create a GitHub repository (backend only) and push `main`.

**Never commit:** `.env` (passwords, connection strings).

**Done when:** Only backend files are on GitHub and `.env` is not in the repo.

---

## Step 4 — Tests

**Goal:** Automated checks that the users API still works after changes.

There are **no tests yet**. For a professional backend, add at least a small smoke suite.

### 4.1 What to add

1. Dev dependency: `pytest` (and usually `httpx`, which FastAPI’s `TestClient` needs).
2. A `tests/` folder, for example:
   - `tests/test_users.py` — create user, list users, get/update/delete
3. Use FastAPI’s `TestClient` against `app.main:app`.
4. Prefer an isolated test database (or override `get_db`) so tests do not wipe your real `crud_db`.

### 4.2 Run tests locally

```bash
poetry run pytest
```

**Done when:** `pytest` passes on your machine for the main user CRUD paths.

---

## Step 5 — Continuous Integration (CI)

**Goal:** Every push / pull request to GitHub automatically installs the backend and runs tests.

**CI = Continuous Integration** — merge only after automated checks pass.

### 5.1 What you will add

A workflow file at this backend repo’s root:

```text
.github/workflows/ci.yml
```

### 5.2 What the CI job should do

1. Check out the repo
2. Set up Python 3.11
3. Install Poetry
4. `poetry install` (repo root is already the backend)
5. `poetry run pytest`

### 5.3 When it runs

- On push to `main`
- On pull requests

**Done when:** Opening a PR or pushing to GitHub shows a green (or red) CI check for the backend.

---

## Step 6 — Deploy backend on Render (CD)

**Goal:** API + Postgres live on the internet. Pushes to `main` can redeploy automatically.

**CD = Continuous Deployment** — on Render this is usually **auto-deploy from GitHub**, not a custom deploy script.

### 6.1 Create a PostgreSQL database on Render

1. Render Dashboard → **New** → **PostgreSQL**
2. Create the database
3. Copy the **Internal** or **External** Database URL (you will paste this into the web service as `DATABASE_URL`)

Note: Render may give `postgres://...`. If SQLAlchemy complains, change the scheme to `postgresql://...`.

### 6.2 Create a Web Service for the API

1. Render Dashboard → **New** → **Web Service**
2. Connect your GitHub repo
3. Settings:

| Setting | Value |
|---------|--------|
| Root Directory | *(leave empty — this repo is the backend)* |
| Runtime | Python |
| Build Command | `pip install poetry && poetry install --no-root` |
| Start Command | `poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### 6.3 Environment variables on the Web Service

| Variable | Value |
|----------|--------|
| `DATABASE_URL` | Connection string from the Render Postgres instance |
| `CORS_ORIGINS` | `http://localhost:5173` for now; later add your frontend URL |

### 6.4 Turn on auto-deploy

Enable auto-deploy from the `main` branch.

Flow:

```text
git push origin main
    → GitHub Actions CI runs (Step 5)
    → Render pulls main and redeploys the API (this step)
```

### 6.5 Verify production

1. Open `https://YOUR-SERVICE.onrender.com/docs`
2. Create a user via Swagger
3. Confirm data persists (refresh / list again)

**Free tier note:** The service may sleep after idle time; the first request can be slow while it wakes up.

**Done when:** `/docs` works on Render and CRUD persists in Render Postgres.

---

## Environment variables reference

| Variable | Where | Purpose |
|----------|--------|---------|
| `DATABASE_URL` | Backend | PostgreSQL connection string |
| `CORS_ORIGINS` | Backend | Allowed browser origins (comma-separated) |

Local example (`.env`):

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/crud_db
CORS_ORIGINS=http://localhost:5173
```

---

## Suggested order (do not skip)

```text
Step 1  Local run works
   ↓
Step 2  CORS + DB init safe for cloud
   ↓
Step 3  Code on GitHub
   ↓
Step 4  pytest passes locally
   ↓
Step 5  GitHub Actions runs pytest
   ↓
Step 6  API live on Render with auto-deploy
```

Frontend deploy (static site + `VITE_API_URL`) is a **separate** guide after the backend is live.

---

## Asking for help

Work through the checklist yourself. When you want the agent to implement something, say the step clearly, for example:

- “Do Step 2 — production readiness”
- “Help me write the pytest tests for Step 4”
- “Create the GitHub Actions workflow for Step 5”
