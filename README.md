# Search a Group Chat Properly

A take-home assessment project for semantic search over a synthetic group chat of at least 4,000 messages from 8 participants across approximately 6 months. The planned React and FastAPI application will combine multilingual embeddings, lexical search, and person/time-aware ranking to return matching messages with conversation context, evaluated against 40 manually labelled queries.

Implemented: the initial React/Vite and FastAPI scaffold, the synthetic corpus and its validator, **40 frozen evaluation queries**, and a local word/character TF-IDF lexical retrieval baseline with an evaluation runner. The corpus contains **4,634 messages from exactly eight fictional Indian students**, covering March 1 through August 31, 2026. Embeddings, hybrid/person/time ranking, surrounding-context assembly and the search API/UI remain future work. See [AGENTS.md](AGENTS.md) for mandatory requirements and [PLAN.md](PLAN.md) for future work.

## Structure

```text
frontend/           React/Vite application and health-client tests
backend/
  app/              FastAPI scaffold and modular lexical retrieval in search/
  scripts/          Offline corpus generator, content, configuration and validator
  tests/            Corpus validation/determinism, health and CORS tests
  data/             Synthetic JSONL, corpus metadata and review notes
evaluation/         Frozen labels, validation, metrics, benchmark runner and tests
results/            Measured lexical benchmark and per-query results
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
- Metadata records participant profiles, counts, seed/configuration, interpreter version, SHA-256, and thread ranges, membership and conclusion IDs. Thread annotations support corpus review and must not become answer lookup rules in future retrieval. Evaluation labels are stored separately under `evaluation/` and are never generator or retrieval inputs.
- JSONL serialization is UTF-8 with LF endings and fixed key order. Tests generate both files independently twice and compare their bytes; they also compare the stored corpus with a fresh generation. Reproduction was verified on Python 3.9.10; other Python versions have not been tested. Changing content or the seed can change IDs and hashes. No embedding model is used, so no model revision applies in this phase.

The three extended threads end in a Manali trip, a React/Vite + FastAPI + SQLite hackathon stack, and a July 25 birthday at Nukkad Cafe costing Rs 2,900. Each includes alternatives, interruptions and follow-up over six dates. See [corpus review notes](backend/data/CORPUS_REVIEW.md) for exact message ranges and conclusions.

This is deliberately synthetic, template-based data: repeated background phrasing and simplified student routines remain limitations. The corpus is not evidence about real students, venues, prices or events, and no private chat was used.

## Frozen retrieval evaluation queries

[evaluation/queries.json](evaluation/queries.json) is a JSON array of exactly 40 manually composed query records: **20 semantic, 10 person and 10 time**. Each includes the requested ID, query text, actual target message ID, primary category, overlap flag and labelling rationale. Queries cover all three decision threads plus exam notices, class changes, volunteer material, travel and an upload problem. Person queries use the actual eight-participant corpus; no nonexistent example name was inserted.

**10 queries (Q001-Q010) have zero meaningful word overlap** with their target text under the fixed [overlap convention](evaluation/OVERLAP.md). Their [manual review](evaluation/HARD_SUBSET_REVIEW.md) explains the semantic connection and nearby distractors. The authoring assistant reviewed the labels; they have not received independent human review. The token audit is exact lexical matching after documented normalization and function-word removal, not a semantic similarity score. Sender/time/context are excluded from the word-overlap calculation.

Time conventions use the corpus reference date **2026-09-01** and Asia/Kolkata: “last month” is August 1-31; “yesterday” is August 31; “morning” is 00:00 through 11:59:59. For these labels, “late April” means April 21-30 and “start of May” means May 1-7. Chat timestamps determine date filtering; a June event mentioned in a March message is still a March chat message. These conventions are documented labels, not an implemented natural-language date parser.

There are **37 distinct target IDs**: each of the three final decisions is tested once semantically and once with a time constraint. All ten hard cases are semantic queries from the decision threads, so the hard subset does not separately measure person/time retrieval. Some targets need nearby context to resolve pronouns, but the target itself carries the requested answer. A neighbor or summary alone must not count as a correct hit.

Run validation from the repository root:

```powershell
.\backend\.venv\Scripts\python.exe -m evaluation.validate_queries
.\backend\.venv\Scripts\python.exe -m evaluation.validate_queries --show-overlap
.\backend\.venv\Scripts\python.exe -m pytest evaluation/tests -q
```

Validation enforces the exact count/schema, real target IDs, categories, at least eight hard labels, nonempty content and agreement of **every** overlap flag with the checker. Default validation also verifies the [freeze manifest](evaluation/freeze_manifest.json) against the unchanged corpus, corpus metadata, labels, convention and review artifacts. It never updates them. `--draft` is only for pre-freeze label review and skips integrity checks; it is not proof that a set is frozen.

Version `1.0.0` was frozen before search implementation or scoring. [label_changes.md](evaluation/label_changes.md) records initial review and the correction procedure. Future legitimate corrections require visible history, versioned artifacts and rerunning affected comparisons; never rewrite expected answers to fit retrieved results. The retrieval module does not read labels; the evaluator supplies only query text and K to it. The initial freeze manifest's `retrieval_scored: false` records the state at freeze time and remains unchanged after later benchmark runs. Scoring reports both Top-1 numerators and denominators (40 overall, 10 hard) and their signed percentage-point gap.

Evaluation-phase checks: validator passed with `freeze_verified: true`; **20 evaluation tests passed** on Python 3.9.10. Corpus and metadata SHA-256 values remained unchanged. Backend/frontend implementation was unchanged, so their existing tests were not rerun in this phase.

## Lexical retrieval baseline

The backend's `app/search/` package separates corpus loading from retrieval. Its [scikit-learn TF-IDF vectorizers](https://scikit-learn.org/1.6/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) use word unigrams/bigrams and character n-grams of length 3-5 within word boundaries (`char_wb`). Each channel uses L2 normalization, smoothed IDF and sublinear term frequency. The fixed lexical score is **0.7 × word cosine + 0.3 × character cosine**. These defaults were chosen before benchmark scoring and are not tuned against the evaluation set.

Only original message `text` is indexed. Sender, timestamp, message IDs, thread/conclusion annotations, query categories, overlap flags and labelling notes are excluded from features. No embeddings, synonym expansion, stopword list or person/date parser is used. The evaluation overlap convention is used only to validate labels, not to preprocess retrieval queries.

The index is built in memory on construction, without a downloaded model or persistent index cache. `search(query, top_k=5)` returns up to K positive-scoring `SearchResult` objects with `id`, `sender`, `timestamp`, original `text` and `lexical_score`; `.to_dict()` serializes one result. Blank or fully out-of-vocabulary queries return an empty list; invalid K values raise an error. Equal scores are ordered by message ID. Character features offer some typo tolerance, but do not provide semantic understanding.

Example, in Python with `backend` as the working directory:

```python
from app.search import LexicalSearch

searcher = LexicalSearch.from_jsonl()
for hit in searcher.search("trip budjet", top_k=3):
    print(hit.to_dict())
```

Install the updated locked dependencies and run the benchmark from the repository root:

```powershell
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock.txt
.\backend\.venv\Scripts\python.exe evaluation/evaluate.py --method lexical
```

With that environment's Python on PATH, the equivalent command is:

```text
python evaluation/evaluate.py --method lexical
```

No running backend/frontend service is needed. The runner validates frozen labels and hashes before and after retrieval, prints aggregate metrics and every incorrect Top-1 query with expected/retrieved text and IDs, and saves [results/lexical.json](results/lexical.json). The JSON includes raw numerators/denominators, rates and percentages, per-category accuracy, the signed overall-minus-hard gap, all top-three messages/scores, configuration, dependency versions, and input/source hashes. Re-running the command overwrites this result file with the new measured run; its UTC measurement time changes.

Top-1 requires the exact expected message ID. Recall@3 is the fraction of queries whose single expected target appears in the first three hits; a short/empty hit list still counts in the denominator. Surrounding context and alternate messages are not credited. Person/time queries are evaluated unchanged even though this baseline cannot interpret their metadata constraints. Zero-word-overlap queries can still have character n-gram or function-word overlap, so a nonzero lexical score does not contradict their hard labels.

Measured lexical results on the frozen version 1.0.0 corpus and query set:

| Metric | Correct / total | Result |
| --- | ---: | ---: |
| Overall Top-1 | 9 / 40 | 22.5% |
| Recall@3 | 16 / 40 | 40.0% |
| Hard zero-overlap Top-1 | 0 / 10 | 0.0% |
| Semantic-category Top-1 | 3 / 20 | 15.0% |
| Person-category Top-1 | 3 / 10 | 30.0% |
| Time-category Top-1 | 3 / 10 | 30.0% |

The signed **overall minus hard Top-1 gap is +22.5 percentage points**. These are measured results, not targets. All 31 incorrect queries were printed with expected and retrieved messages; all 40 rankings are saved in the JSON. For example, Q015 retrieves the question about outside cake instead of the answer giving permission and decoration conditions. Q017 retrieves an identical exam forward from April instead of the labelled May message, although the correct ID is in its top three. Generic question words also produce unrelated matches when substantive query terms are absent. No settings or labels were changed after observing these results.

This run used Python 3.9.10, scikit-learn 1.6.1, NumPy 2.0.2 and SciPy 1.13.1 on Windows; complete dependency versions and source/input hashes are in the result artifact. Tiny floating-point differences on other platforms are possible. Only the lexical method is measured; the full three-method comparison remains future work.

Lexical-phase checks: **51 backend tests and 25 evaluation tests passed** (76 total); `pip check` found no broken requirements. Tests cover typo recovery with zero word-feature matches, stable ties, empty/OOV queries, original result fields, exclusion of metadata from features, malformed corpus input, known metric rankings and denominators, label isolation and frozen integrity. The benchmark ran successfully through the exact `evaluation/evaluate.py --method lexical` entry point. Saved per-query rankings were independently checked against aggregate counts and source/input/lock hashes. The frontend was unchanged, so its tests were not rerun.

## Checks

From the repository root:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
cd ..
.\backend\.venv\Scripts\python.exe -m pytest evaluation/tests -q
cd frontend
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
