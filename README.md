# Search a Group Chat Properly

A take-home assessment project for semantic search over a synthetic group chat of at least 4,000 messages from 8 participants across approximately 6 months. The planned React and FastAPI application will combine multilingual embeddings, lexical search, and person/time-aware ranking to return matching messages with conversation context, evaluated against 40 manually labelled queries.

Only the initial application scaffold is implemented: React with Vite and JavaScript, plain responsive CSS, a FastAPI health endpoint, and a frontend backend-connection indicator with a retry button. Search, dataset generation, data contracts, embeddings, indexing, and evaluation are not implemented. No benchmark results have been measured. This completes only the scaffolding portion of Phase 1. See [AGENTS.md](AGENTS.md) for mandatory requirements and [PLAN.md](PLAN.md) for future work.

## Structure

```text
frontend/           React/Vite application and health-client tests
backend/
  app/              FastAPI entry point, configuration, and API routes
  scripts/          Reserved for future scripts
  tests/            Health and CORS tests
  data/             Reserved for future synthetic data
evaluation/         Reserved for future evaluation code and labels
results/            Reserved for future measured results
```

Empty directories contain only `.gitkeep` placeholders.

## Prerequisites

- Node.js 20.19+ on the 20.x line, or 22.12+; npm. See the [Vite setup guide](https://vite.dev/guide/).
- Python 3.9 or newer with pip and venv. The initial backend dependencies support the Python 3.9 runtime available on this machine.
- Internet access for the first dependency installation. This scaffold needs no secrets, LLM API, model download, or dataset.

Commands below use Windows PowerShell, starting from the repository root. `npm.cmd` avoids PowerShell script execution-policy restrictions; on macOS/Linux use `npm`. There is no need to activate the Python environment.

## Start the backend

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

`requirements.txt` pins direct runtime and test dependencies. `requirements.lock.txt` records the full tested environment; use it for reproducible installation. On macOS/Linux create the environment with `python3 -m venv .venv` and replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`.

Health: `GET http://127.0.0.1:8000/api/health` returns HTTP 200 and `{"status":"ok"}`. API docs: `http://127.0.0.1:8000/docs`.

## Start the frontend

In a second terminal, from the repository root:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Open `http://127.0.0.1:5173`. The page calls `/api/health` on mount and displays `Backend connected` when the backend responds successfully. Failures or a five-second timeout display a disconnected message; use **Check again** after starting the backend.

Vite forwards `/api` to `http://127.0.0.1:8000`. Port 5173 is fixed; stop a conflicting process or update the Vite and backend origin settings together. FastAPI allows CORS from `http://localhost:5173` and `http://127.0.0.1:5173`, following the [FastAPI CORS configuration](https://fastapi.tiangolo.com/tutorial/cors/). These are local development settings. Production hosting and API routing are not configured in this phase; `npm.cmd run build` produces frontend assets only.

## Checks

From the repository root:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
cd ../frontend
npm.cmd test
npm.cmd run build
```

With both services running, verify direct and proxied health responses:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:5173/api/health
```

Validation performed on Windows with Node.js 24.8.0, npm 11.6.0, and Python 3.9.10:

- Backend: 5 pytest tests passed (health response, both local CORS origins and preflights, rejection of an unlisted origin, and absence of a search route).
- Frontend: 4 health-client tests passed (success, HTTP failure, unexpected payload, and connection failure).
- `npm.cmd run build` passed; `pip check` found no broken requirements.
- Live requests to both port 8000 and port 5173 `/api/health` returned HTTP 200 with `{"status":"ok"}`; Vite served the frontend HTML successfully.
- `git diff --check` passed. Initial sandbox attempts blocked the build temporary directory and access to Python; approved reruns passed.
- Browser automation was unavailable, so the rendered status display and retry interaction were not visually verified. Test servers were stopped after verification.
