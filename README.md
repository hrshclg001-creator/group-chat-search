# Search a Group Chat Properly

A take-home assessment project for semantic search over a synthetic group chat of at least 4,000 messages from 8 participants across approximately 6 months. The planned React and FastAPI application will combine multilingual embeddings, lexical search, and person/time-aware ranking to return matching messages with conversation context, evaluated against 40 manually labelled queries.

Implemented: the initial React/Vite and FastAPI scaffold, plus a deterministic synthetic chat generator and corpus validator. The corpus contains **4,634 messages from exactly eight fictional Indian students**, covering March 1 through August 31, 2026. Search, embeddings, indexing, evaluation queries, and benchmarks are not implemented. Phase 1's remaining API/evaluation data contracts remain future work. See [AGENTS.md](AGENTS.md) for mandatory requirements and [PLAN.md](PLAN.md) for future work.

## Structure

```text
frontend/           React/Vite application and health-client tests
backend/
  app/              FastAPI entry point, configuration, and API routes
  scripts/          Offline corpus generator, content, configuration and validator
  tests/            Corpus validation/determinism, health and CORS tests
  data/             Synthetic JSONL, corpus metadata and review notes
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

## Generate and validate the synthetic chat

The generated files are included in the repository. To reproduce them, from the repository root:

```powershell
cd backend
.\.venv\Scripts\python.exe -m scripts.generate_data
.\.venv\Scripts\python.exe -m scripts.validate_data
.\.venv\Scripts\python.exe -m pytest
```

The generator and validator use only the Python standard library; they need no network, model, or additional packages. You can also run them with `py -3 -m scripts.generate_data` and `py -3 -m scripts.validate_data` from `backend`. Their default paths are resolved relative to the script package. `--output-dir PATH` on the generator and `--data-dir PATH` on the validator support separate reproduction folders.

- Output: [messages.jsonl](backend/data/messages.jsonl) and [corpus_metadata.json](backend/data/corpus_metadata.json).
- Fixed seed: `20260901`; generator version: `1.0.0`; reference runtime: Python `3.9.10`. The full tested backend dependency versions remain in `backend/requirements.lock.txt`.
- Inclusive dates: `2026-03-01` through `2026-08-31` (184 dates). Timestamps are chronological ISO 8601 strings with the `+05:30` offset, corresponding to Asia/Kolkata.
- Fixed reference date: `2026-09-01`, stored in the metadata for later relative-time interpretation. Relative-date search is not implemented yet.
- Each row has `id`, `timestamp`, `sender` (full name), `text`, `message_type`, and `metadata` containing stable `participant_id`, `topic`, and `episode_id`. Decision messages also have `thread_id`. IDs run from `MSG_000001` to `MSG_004634` and are stable for this seed, content and configuration.
- Types: `text`, `forwarded`, `url`, `image`, `pdf`, `voice`. Media are text placeholders, not actual attachments. Example-domain links are placeholders; no link is fetched during generation.
- Composition: 552 complete daily conversations (2-4 per day, eight messages each), 216 hand-authored decision messages, and two boundary messages. Background conversations use 56 season-aware vignettes with shared details, changing speakers, wording variations and irregular reply intervals.
- Metadata records participant profiles, counts, seed/configuration, interpreter version, SHA-256, and thread ranges, membership and conclusion IDs. Thread annotations support corpus review and must not become answer lookup rules in future retrieval. No evaluation labels exist yet.
- JSONL serialization is UTF-8 with LF endings and fixed key order. Tests generate both files independently twice and compare their bytes; they also compare the stored corpus with a fresh generation. Reproduction was verified on Python 3.9.10; other Python versions have not been tested. Changing content or the seed can change IDs and hashes. No embedding model is used, so no model revision applies in this phase.

The three extended threads end in a Manali trip, a React/Vite + FastAPI + SQLite hackathon stack, and a July 25 birthday at Nukkad Cafe costing Rs 2,900. Each includes alternatives, interruptions and follow-up over six dates. See [corpus review notes](backend/data/CORPUS_REVIEW.md) for exact message ranges and conclusions.

This is deliberately synthetic, template-based data: repeated background phrasing and simplified student routines remain limitations. The corpus is not evidence about real students, venues, prices or events, and no private chat was used.

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

Latest dataset-phase validation on Windows / Python 3.9.10: generator and standalone validator passed; **32 backend tests passed** (27 corpus tests plus the existing 5 health/CORS tests). Checks include minimum count, participants, date coverage, IDs, content varieties, all three long decisions, deterministic bytes, artifact consistency, and rejection of corrupted records/files. An initial generation attempt correctly failed because the literal one-word reply `ok` was missing; the content was corrected and generation and tests rerun successfully. No frontend code changed in this phase, so its checks were not rerun.

Previous scaffold-phase validation used Node.js 24.8.0, npm 11.6.0, and Python 3.9.10:

- Backend: 5 pytest tests passed (health response, both local CORS origins and preflights, rejection of an unlisted origin, and absence of a search route).
- Frontend: 4 health-client tests passed (success, HTTP failure, unexpected payload, and connection failure).
- `npm.cmd run build` passed; `pip check` found no broken requirements.
- Live requests to both port 8000 and port 5173 `/api/health` returned HTTP 200 with `{"status":"ok"}`; Vite served the frontend HTML successfully.
- `git diff --check` passed. Initial sandbox attempts blocked the build temporary directory and access to Python; approved reruns passed.
- Browser automation was unavailable, so the rendered status display and retry interaction were not visually verified. Test servers were stopped after verification.
