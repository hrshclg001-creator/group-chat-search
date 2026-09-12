# Search a Group Chat Properly

A take-home assessment project for semantic search over a synthetic group chat of at least 4,000 messages from 8 participants across approximately 6 months. The planned React and FastAPI application will combine multilingual embeddings, lexical search, and person/time-aware ranking to return matching messages with conversation context, evaluated against 40 manually labelled queries.

Implemented: the React/Vite scaffold, FastAPI health/search/stats endpoints, synthetic corpus, **40 frozen evaluation queries**, lexical/semantic/contextual baselines, a deterministic person/time parser, and hybrid retrieval with metadata constraints. The corpus contains **4,634 messages from exactly eight fictional Indian students**, covering March 1 through August 31, 2026. Hybrid Top-1 is **21/40 (52.5%)**, measured on the same queries used to select its weights. Search results include the original matching message and up to three chronological neighbors per side. The frontend search interface remains future work. See [AGENTS.md](AGENTS.md) for mandatory requirements and [PLAN.md](PLAN.md) for future work.

## Structure

```text
frontend/           React/Vite application and health-client tests
backend/
  app/              FastAPI scaffold and modular lexical/semantic retrieval in search/
  scripts/          Corpus generation/validation and pinned model preparation
  tests/            Corpus, retrieval, cache, real-model, health and CORS tests
  data/             Synthetic JSONL, corpus metadata and review notes
evaluation/         Frozen labels, validation, metrics, benchmark runner and tests
results/            Measured retrieval benchmarks, rankings and comparisons
```

Empty directories contain only `.gitkeep` placeholders.

## Prerequisites

- Node.js 20.19+ on the 20.x line, or 22.12+; npm. See the [Vite setup guide](https://vite.dev/guide/).
- Python 3.9 or newer with pip and venv. The initial backend dependencies support the Python 3.9 runtime available on this machine.
- Internet access for the first dependency installation and semantic model preparation. Normal inference is local and requires no secrets or external LLM API. Lexical retrieval needs no model download.

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

Search also requires the one-time local model preparation documented below. Startup loads the corpus and initializes one shared hybrid index per server process, using existing embedding caches or building missing caches once. Allow startup to finish before making requests. If model/index preparation fails, health and corpus stats remain available but search returns HTTP 503 with setup instructions; fix the startup error and restart. No model downloads or document embedding generation happen inside the search request handler.

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

This run used Python 3.9.10, scikit-learn 1.6.1, NumPy 2.0.2 and SciPy 1.13.1 on Windows; complete dependency versions and source/input hashes are in the result artifact. Tiny floating-point differences on other platforms are possible. Subsequent semantic/contextual and hybrid comparisons are below.

Lexical-phase checks: **51 backend tests and 25 evaluation tests passed** (76 total); `pip check` found no broken requirements. Tests cover typo recovery with zero word-feature matches, stable ties, empty/OOV queries, original result fields, exclusion of metadata from features, malformed corpus input, known metric rankings and denominators, label isolation and frozen integrity. The benchmark ran successfully through the exact `evaluation/evaluate.py --method lexical` entry point. Saved per-query rankings were independently checked against aggregate counts and source/input/lock hashes. The frontend was unchanged, so its tests were not rerun.

## Contextual semantic retrieval

`app/search/context.py` computes one representation per original message. It takes at most the two immediately previous and two immediately following messages in chronological order, with a maximum distance of 30 minutes from the current message. It does not jump over messages to find matching topics or use thread/episode/conclusion annotations. At corpus boundaries or across long gaps, fewer neighbors are included. Following messages are appropriate for this completed archive; this is not a causal live-chat model.

Every contextual hit contains `id`, `sender`, `timestamp`, `text`, `original_text`, `semantic_score`, `context_text`, `context_message_ids`, `context_messages`, `embedding_text` and `truncated_message_ids`. Both `text` and `original_text` are the exact original current message. `context_message_ids` includes the current message and at most four neighbors. Display context messages carry `is_current`; matching a neighbor never changes the result's target ID or earns evaluation credit for that neighbor.

The pinned [multilingual MiniLM model](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) is `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` at revision `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`. It runs on CPU with four threads and normalized float32 embeddings; ranking uses NumPy cosine similarity and stable ID tie-breaking. No sender/date boosts are added. Model revision and downloaded-file hashes are recorded in each semantic result artifact.

Both semantic methods use an explicit **256-token maximum**, increased from the model package's 128-token sentence setting to accommodate the bounded conversation. Context text uses Previous/Current/Following message markers. When embedding input is too long, the longest neighbors are trimmed first; only a current message that cannot fit by itself is truncated for embedding. Full originals and full bounded `context_text` are retained separately. `embedding_text` records the exact string passed to the encoder, and result configuration reports truncation counts. These limits were fixed before scoring.

Prepare the public model once (approximately 450 MB of weights, plus tokenizer files; PyTorch dependencies also require disk space):

```powershell
# From the repository root:
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock.txt
cd backend
.\.venv\Scripts\python.exe -m scripts.prepare_model
cd ..
.\backend\.venv\Scripts\python.exe evaluation/evaluate.py --method semantic
.\backend\.venv\Scripts\python.exe evaluation/evaluate.py --method contextual
.\backend\.venv\Scripts\python.exe -m evaluation.compare
```

With the environment activated, the requested command is `python evaluation/evaluate.py --method contextual`. `semantic` is the original-text-only control using the same model and token limit; it isolates the effect of adding context. Comparing contextual embeddings only against lexical retrieval would also include the effect of changing retrieval models.

The download script fetches only pinned tokenizer/configuration files and safetensors weights into ignored `.cache/models/`. Model loading uses `local_files_only=True` and disables remote code. Re-running preparation verifies file hashes; interrupted downloads leave only a `.part` file. Inference never downloads files. Encodings are cached under `.cache/embeddings/` by exact representation text, model revision/file hashes, settings and dependency versions, with shape/norm/checksum validation. Repeated evaluations reuse these caches; changed corpus text, context text or model settings create new keys.

Results are saved separately in `results/semantic.json` and `results/contextual.json`. The comparison command verifies identical frozen inputs, recomputes aggregate metrics from stored ranks, and writes `results/contextual_comparison.json`, including category gains/losses and newly correct/incorrect query IDs. The existing lexical artifact is preserved. Neighbor-only matches are reported diagnostically but remain wrong under strict target-ID scoring.

Short replies such as `done`, `haan pakka`, `this one` and `ok final` have unit tests for contextual representation and unchanged target display. Optional offline real-model tests also verify that identical short replies in different conversations acquire distinct representations. These examples are test fixtures; the 40 frozen benchmark targets are not replaced with easier short-reply labels, and no separate short-reply accuracy is claimed.

Measured results on the same frozen 40 queries and 4,634 messages:

| Metric | Lexical (previous run) | Original-only semantic | Contextual | Contextual minus semantic |
| --- | ---: | ---: | ---: | ---: |
| Overall Top-1 | 9/40 (22.5%) | 13/40 (32.5%) | 4/40 (10%) | -22.5 pp |
| Recall@3 | 16/40 (40%) | 16/40 (40%) | 12/40 (30%) | -10 pp |
| Hard zero-overlap Top-1 | 0/10 (0%) | 1/10 (10%) | 1/10 (10%) | 0 pp |
| Semantic-category Top-1 | 3/20 (15%) | 6/20 (30%) | 1/20 (5%) | -25 pp |
| Person-category Top-1 | 3/10 (30%) | 3/10 (30%) | 1/10 (10%) | -20 pp |
| Time-category Top-1 | 3/10 (30%) | 4/10 (40%) | 2/10 (20%) | -20 pp |
| Overall minus hard Top-1 gap | +22.5 pp | +22.5 pp | 0 pp | |

**Adding this context window made every category worse.** It gained Q024 but lost ten previously correct queries relative to original-only semantic retrieval. Hard-subset accuracy stayed at 1/10; its improvement over lexical retrieval cannot be attributed to context. No parameters or expected answers were changed after scoring.

In 11 incorrect contextual Top-1 results, the expected answer appears only in the returned target's surrounding context. For example, Q013 expects the birthday decision `MSG_003616`, but the returned target is `MSG_003618`, a cake-pickup follow-up whose context includes that decision. It remains incorrect. Similar representations across adjacent messages can find the right conversation while failing to select its actual answer. Context also introduces distractors. Those runs used no person/time parser or reranker. Neither semantic run truncated any of this corpus's embedding inputs at the configured 256-token limit.

Artifacts: [semantic results](results/semantic.json), [contextual results](results/contextual.json), and [comparison with query-level changes](results/contextual_comparison.json). They record configuration, pinned model/file hashes, dependency versions, matrix checksums and all rankings. The corpus, metadata, frozen query/review files and previous lexical artifact are unchanged.

Contextual-phase checks on Windows / Python 3.9.10: **67 backend tests and 28 evaluation tests passed (95 total)**, including all four offline real-model short-reply cases. `pip check` passed. Both semantic benchmarks and the comparison completed; saved metrics and artifact hashes were verified. The initial model download hit a CDN DNS failure; a retry using explicit download URLs completed successfully. Frontend code was unchanged, so its tests/build were not rerun in this phase. This validates the implementation, not an accuracy improvement.

## Standalone person/time query parser

`backend/app/query_understanding/` uses only the Python standard library. It reads participant names, `reference_date` and timezone from corpus metadata; it does not load messages, evaluation labels, a model or an index, call an external API, or change ranking. The raw query is preserved. Example usage from `backend`:

```python
from app.query_understanding import QueryParser

parser = QueryParser.from_metadata()
print(parser.parse("Ishita ne last month budget pe kya bola?").to_dict())
```

```json
{
  "raw_query": "Ishita ne last month budget pe kya bola?",
  "person": "Ishita Patel",
  "start_date": "2026-08-01",
  "end_date": "2026-08-31",
  "intent": "person_time_semantic",
  "reference_date": "2026-09-01",
  "timezone": "Asia/Kolkata",
  "person_candidates": ["Ishita Patel"],
  "warnings": []
}
```

Run the parser directly, with one or more quoted queries, from `backend`:

```powershell
.\.venv\Scripts\python.exe -m app.query_understanding "What did Ishita say about the budget?" "Rohan ne last month kya bola?"
.\.venv\Scripts\python.exe -m pytest tests/test_query_parser.py -q
```

`--metadata PATH` selects another metadata file. Missing/invalid reference dates fail explicitly; the parser never falls back to the machine's date. Date bounds are inclusive calendar dates in the metadata timezone and are not clipped to the corpus. Thus `today` is September 1 even though the corpus ends August 31.

Rules fixed for this implementation:

- Participant matching uses Unicode normalization, case-insensitive whole-name boundaries and full/first/last names from metadata. A unique match returns the canonical full name. Longer full names disambiguate shared aliases; multiple distinct matches return `person: null`, candidates and a warning. Known name mentions are detected without distinguishing sender, recipient or topic. Unknown names remain unresolved; Priya/Rahul/Aman are example test participants, not members added to this corpus.
- `today`/`aaj` means the reference date; `yesterday`/`beete kal` means the previous date. `last week`/`pichle hafte` means the previous complete Monday-Sunday, August 24-30 here. `last month`/`pichle mahine` means the previous complete calendar month; `this month`/`is mahine` means the reference calendar month. The `pichhle` spelling is also supported. Bare `kal` is ambiguous and yields a warning with no date bounds.
- English month names and three-letter abbreviations (also `sept`) use the reference year when no year is supplied, even for months after September. Bare `May` works by itself; within a sentence it needs a month cue such as `in May`, `May mein` or a day/year to avoid treating auxiliary `may` as a date.
- Supported dates are ISO `YYYY-MM-DD`, `15 August 2026`, and `August 15, 2026`, with optional ordinals and optional year for named dates. Simple ranges include `2026-03-01 to 2026-03-10`, `between 1 June and 15 July 2026`, `1-15 August`, `August 1-15`, and `1 Aug se 15 Aug tak`. `through`, `until` and dash connectors are inclusive too. A single explicit year applies to both range endpoints; cross-year ranges require both years explicitly.
- Compatible time expressions intersect. Conflicting intervals, invalid/reversed dates, or ambiguous numeric slash dates return null date bounds and warnings. Unsupported linguistic constructions (negation, event-relative dates, time of day, and fine-grained qualifiers such as `late April`) are not fully interpreted; a recognized month alone yields that whole month. This is a bounded rule grammar, not general language understanding. Consumers must review warnings before applying future filters.
- Intent is `semantic`, `person_semantic`, `time_semantic` or `person_time_semantic`, based on resolved constraints. Hybrid retrieval now consumes these parsed constraints through the conservative sender/date interpretation described below; the three baselines remain unchanged.

Actual CLI examples, all using reference date `2026-09-01` and timezone `Asia/Kolkata` (all warnings empty):

| Raw query | Person | Inclusive start / end | Intent |
| --- | --- | --- | --- |
| What did Ishita say about the budget? | Ishita Patel | null / null | person_semantic |
| Rohan ne last month trip ke baare mein kya bola? | Rohan Mehta | 2026-08-01 / 2026-08-31 | person_time_semantic |
| Message from Aarav about coding yesterday | Aarav Sharma | 2026-08-31 / 2026-08-31 | person_time_semantic |
| Sneha ne aaj kya bola? | Sneha Iyer | 2026-09-01 / 2026-09-01 | person_time_semantic |
| What did we decide last week? | null | 2026-08-24 / 2026-08-30 | time_semantic |
| Meera ke this month wale messages | Meera Nair | 2026-09-01 / 2026-09-30 | person_time_semantic |
| Ananya ne August mein exams ke baare mein kya bola? | Ananya Verma | 2026-08-01 / 2026-08-31 | person_time_semantic |
| Messages from Kabir between 1 June and 15 July 2026 | Kabir Khan | 2026-06-01 / 2026-07-15 | person_time_semantic |

Parser-phase validation: **71 parser tests passed**, and the full suites passed with **138 backend tests plus 28 evaluation tests (166 total)**. Cases include English/Hinglish patterns, ambiguous aliases/dates, leap years, week/year boundaries, custom metadata and a wall-clock guard. Ten CLI examples ran successfully. Initial sandbox attempts to launch two Python commands could not access the installed runtime; authorized reruns passed. Retrieval code, frozen data/labels and benchmark artifacts are unchanged; no ranking evaluation or frontend checks were rerun for this parsing-only phase.

## Hybrid retrieval and four-method comparison

`backend/app/search/hybrid.py` combines the existing original-only semantic, contextual semantic and lexical indexes. One pinned local encoder is shared, and the existing embedding caches are reused. It scores every corpus message before applying constraints and selecting top K. Evaluation labels, expected IDs, notes, categories and thread/conclusion annotations never enter retrieval. Original raw query text supplies all similarity channels.

`constraints.py` consumes the standalone parser and distinguishes explicit sender language (`what did NAME say`, `NAME ne`, `from NAME`, `NAME shared`) from a bare name mention. Clear single-sender requests **filter the current author**. A known name without a clear sender role gets a small bonus; names used as topics or recipients and ambiguous/multiple names get no sender preference. This conservative rule can miss implicit author intent, as the measured spending-limit example below shows.

Resolved chat dates **exclude current messages outside the inclusive range**, using metadata reference date `2026-09-01` and Asia/Kolkata. Morning is 00:00-11:59:59; other day parts and month-part boundaries are visible in configuration. `late MONTH` uses days 21-end and `start of MONTH`/`early MONTH` uses days 1-7. Date expressions directly attached to event nouns, such as `the June trip`, are not assumed to be message timestamps; another explicit chat date in the same query still applies. These are general rules applied to every query, not benchmark-ID exceptions. Unsupported/ambiguous phrasing remains a limitation. On Windows without an IANA database, the corpus's modern Indian timestamps use explicit UTC+05:30, never the machine timezone.

Person and date filters intersect. An empty intersection returns no hits without relaxing the request. Filters apply to the original current message; its bounded display context may include other authors or dates. Results preserve the actual target ID and original text and include individual semantic/contextual/lexical scores, person/date matches, metadata bonus, final hybrid score, context and an explanation of the applied constraints/weights. A neighboring answer is still wrong under exact-ID scoring.

All weights, the four trial profiles and date-refinement boundaries live in [ranking_config.py](backend/app/search/ranking_config.py). Semantic cosine is clamped to [0,1], TF-IDF uses its existing nonnegative cosine score, and no query-specific min/max normalization is applied. The selected **balanced** profile uses:

| Signal | No hard constraint | Clear author and/or date constraint |
| --- | ---: | ---: |
| Contextual semantic | 0.35 | 0.25 |
| Original semantic | 0.35 | 0.45 |
| Lexical TF-IDF | 0.20 | 0.20 |
| Person bonus, when applicable | 0.05 | 0.05 |
| Date bonus, when applicable | 0.05 | 0.05 |

The constrained route transfers 0.10 from context to the original message to focus ranking within the eligible set. Bonuses are zero when absent, not redistributed. A hard-filter bonus is constant across eligible messages; the filter itself supplies the strong metadata influence. Scores are not calibrated probabilities or intended for comparisons across different queries.

Four profiles were declared before this task's first hybrid scoring. Their base `(contextual, original, lexical)` weights were `(0.55, 0.20, 0.15)`, `(0.35, 0.35, 0.20)`, `(0.20, 0.55, 0.15)` and `(0.10, 0.65, 0.15)`; each used the same metadata policy, bonuses and constrained transfer. The measured selection rule was highest overall Top-1, then Recall@3, then declaration order. [hybrid_tuning.json](results/hybrid_tuning.json) retains all configurations, rankings and measurements:

| Profile | Top-1 | Recall@3 | Hard Top-1 |
| --- | ---: | ---: | ---: |
| context_first (suggested starting mix) | 20/40 (50%) | 25/40 (62.5%) | 1/10 (10%) |
| balanced (selected) | 21/40 (52.5%) | 25/40 (62.5%) | 1/10 (10%) |
| original_first | 21/40 (52.5%) | 25/40 (62.5%) | 1/10 (10%) |
| anchor_first | 20/40 (50%) | 24/40 (60%) | 1/10 (10%) |

Balanced and original_first tied under both metrics; declaration order chose balanced. No category-specific weight selection or per-query answer rules were used. The four-profile comparison was rerun once with the final default to verify reproducibility and record current source hashes; rankings and aggregate results agreed. **These 40 queries are also the tuning set.** The results are development-set measurements, not an independent estimate of generalization; unchanged ground truth alone does not eliminate that limitation.

Measured four-method comparison on the exact same frozen inputs:

| Metric | Lexical | Semantic | Contextual | Hybrid |
| --- | ---: | ---: | ---: | ---: |
| Overall Top-1 | 9/40 (22.5%) | 13/40 (32.5%) | 4/40 (10%) | 21/40 (52.5%) |
| Recall@3 | 16/40 (40%) | 16/40 (40%) | 12/40 (30%) | 25/40 (62.5%) |
| Hard Top-1 | 0/10 (0%) | 1/10 (10%) | 1/10 (10%) | 1/10 (10%) |
| Semantic category | 3/20 (15%) | 6/20 (30%) | 1/20 (5%) | 7/20 (35%) |
| Person category | 3/10 (30%) | 3/10 (30%) | 1/10 (10%) | 7/10 (70%) |
| Time category | 3/10 (30%) | 4/10 (40%) | 2/10 (20%) | 7/10 (70%) |
| Overall minus hard gap | +22.5 pp | +22.5 pp | 0 pp | +42.5 pp |

Against original-only semantic retrieval, hybrid improves semantic-category accuracy by 5 percentage points, person by 40 and time by 30. Overall increases 20 points, but the hard subset stays at 1/10. The larger overall/hard gap reflects better performance on easier metadata-bearing queries, not improved difficult paraphrase understanding. Baseline artifacts are the preserved measured runs with their original configuration/source hashes; the comparison verifies identical input hashes and recomputes all metrics from saved ranks.

There are still 19 Top-1 errors, all printed by the benchmark and retained in [hybrid.json](results/hybrid.json). Examples: Q001 misses the Hinglish/cost rejection despite a related trip match; Q012 and Q032 miss the actual final stack message; Q015 returns the cake-permission question instead of the answer (the answer is third); Q022's weak possessive-person bonus does not overcome another author's Goa estimate (the expected spending limit is second); Q038 returns Meera's later maintenance reminder instead of her forwarded notice (the notice is second). Filtering can find the right author/date while similarity still selects the wrong conversational role. We did not add rules targeting these failures after selecting the profile.

After installing the locked dependencies and preparing the model as above, run from the repository root:

```powershell
.\backend\.venv\Scripts\python.exe evaluation/evaluate.py --method hybrid
.\backend\.venv\Scripts\python.exe -m evaluation.compare --all
# Optional reproduction of the declared tuning experiment; it never edits defaults:
.\backend\.venv\Scripts\python.exe -m evaluation.tune_hybrid
```

With the environment's Python on PATH, the requested command is `python evaluation/evaluate.py --method hybrid`. The benchmark saves [results/hybrid.json](results/hybrid.json); the comparison saves [results/comparison.json](results/comparison.json), including all metrics, signed gaps, category changes, query gains/losses and report hashes. The earlier `python -m evaluation.compare` command still produces only the contextual comparison. No backend server or frontend is required. To use the engine directly from `backend`:

```python
from app.search.corpus import load_corpus
from app.search.hybrid import HybridSearch

searcher = HybridSearch(load_corpus())
for hit in searcher.search("What did Ananya share last month?", top_k=3):
    print(hit.to_dict())
```

Hybrid-phase checks: **all 166 backend tests and 30 evaluation tests passed (196 total)**, including 28 new hybrid tests for sender/date intersections, no-match behavior, UTC/India date boundaries, event vs chat dates, score explanations, ID alignment, ties and original-target context. The final hybrid benchmark and four-method comparison completed. Corpus, labels, metadata, parser and baseline retrieval/artifacts are unchanged. No frontend/API code changed, so frontend checks were not rerun. The tokenizer emits its packaged 128-token warning while context lengths are counted; the encoder explicitly uses the previously documented 256-token limit, and inference/tests completed successfully.

## Search and stats API

`POST /api/search` accepts a nonblank string `query` (up to 2,000 characters) and an integer `top_k` (default 5, range 1-50). Blank/invalid bodies, unexpected fields and invalid K values return HTTP 422. GET on the search route returns 405. Empty metadata-filter intersections return HTTP 200 with `results: []` and the interpreted query still present.

```powershell
$requestBody = @{ query = 'When did we finally choose Manali?'; top_k = 5 } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/search -Method Post -ContentType 'application/json' -Body $requestBody
Invoke-RestMethod http://127.0.0.1:8000/api/stats
```

The response contains `query`, `interpreted_query`, `search_time_ms` and `results`. Each result has:

- `matching_message`: the actual original `id`, `sender`, `timestamp` and `text`.
- `previous_messages` and `next_messages`: up to three immediately adjacent messages on each side, each list in chronological order. The combined order is previous messages, matching message, next messages. Equal timestamps use message-ID ordering. The existing 30-minute maximum distance from the matching message prevents context from spanning unrelated long gaps; corpus boundaries and gaps produce shorter lists. Neighbors can have different authors/dates from the search filters.
- `search_score` (hybrid score), `semantic_score` (original-only semantic), `contextual_score`, `lexical_score`, detected `query_metadata` and a one-based `rank`. Scores are not probabilities.

`interpreted_query` and each hit's `query_metadata` contain the effective person/date constraints, sender mode (`none`, `bonus`, `filter`), intent, participant candidates, hour range, fixed reference date/timezone, parser warnings and explanations. Event dates ignored as chat-date filters are reflected in the effective fields. The raw query is preserved.

Display context is assembled by `app/services/conversation.py` independently of the **unchanged two-neighbor embedding window**. The API never replaces an original hit with its neighbor or changes ranking to generate a better-looking response. `SearchService` belongs to the FastAPI lifespan, so model/corpus/index setup occurs once per process. Only one query embedding is computed per search request. A lock serializes shared encoder access; synchronous search runs in FastAPI's thread pool, while health/stats do not acquire that lock. Reloads or additional worker processes initialize their own instances. `search_time_ms` measures query work, lock waiting and response construction using a monotonic timer; it excludes startup and HTTP transport.

`GET /api/stats` reads the already loaded corpus without inference. Its actual response is:

```json
{
  "message_count": 4634,
  "participant_count": 8,
  "date_range": {
    "start": "2026-03-01T07:05:00+05:30",
    "end": "2026-08-31T23:50:00+05:30"
  },
  "reference_date": "2026-09-01",
  "timezone": "Asia/Kolkata"
}
```

Full JSON captured from a real local HTTP server is included in [search_response.json](examples/search_response.json), [search_filtered_response.json](examples/search_filtered_response.json) and [stats_response.json](examples/stats_response.json). The search examples use `top_k: 1` to keep the artifacts compact. The supplied Manali question actually retrieved `MSG_002538`, an unrelated movie-chat message, in 53.537 ms. That retrieval failure is preserved, not replaced with the intended trip decision. The person/time example about Ananya's August volunteer checklist correctly returns `MSG_003930` in 44.837 ms, with original text and three following messages. These are single observed timings, not performance guarantees.

API-phase checks: **all 191 backend tests and 30 evaluation tests passed (221 total)**. The new API tests cover validation, rank/score parity with direct hybrid retrieval, original targets, display ordering/boundaries, date/person metadata, empty results, OpenAPI, POST CORS and missing-model HTTP 503 behavior. A counting encoder verifies that repeated requests reuse the same matrices and factory instance and encode only query strings. Real HTTP checks on a temporary localhost server verified both endpoints, health and empty results; Q024's API top-three IDs matched the saved direct hybrid benchmark. Document-cache file counts, modification times and SHA-256 values remained unchanged across requests. The temporary server was stopped. Retrieval code, model settings, corpus, frozen labels and benchmark artifacts are unchanged; no ranking benchmark or frontend checks were rerun for this API-only change.

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
