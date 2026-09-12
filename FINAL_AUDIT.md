# Assessment-readiness audit

Audit date: **2026-09-12**. Requirements: [AGENTS.md](AGENTS.md), [PLAN.md](PLAN.md), and the assessment-readiness request.

**Verdict: PASS with WARNINGS.** No unresolved implementation or required-command failure was found in the tested Windows environment. The project is reproducible there, but retrieval quality remains limited and browser interaction checks are unverified. This is not a claim of perfect search, held-out accuracy, or cross-platform certification.

Status meanings: **PASS** = checked and supported by evidence; **FAIL** = observed unmet requirement; **WARNING** = a limitation, incomplete verification, or restricted scope. Resolved initial failures are recorded below rather than hidden. Machine-readable evidence: [results/audit_evidence.json](results/audit_evidence.json).

## Corpus

| Requirement | Status | Evidence |
| --- | --- | --- |
| Synthetic corpus; no real/private chat | PASS | Generator uses authored fictional conversation templates and a fixed seed. Independent generation in the fresh installation reproduced both corpus and metadata byte-for-byte. No private-chat import is required. |
| At least 4,000 messages | PASS | **4,634** JSONL records; validator and backend tests pass. |
| Exactly 8 realistic participants | PASS | Aarav Sharma, Aditya Joshi, Ananya Verma, Ishita Patel, Kabir Khan, Meera Nair, Rohan Mehta and Sneha Iyer. These are explicitly fictional students. |
| Approximately six months | PASS | **2026-03-01 through 2026-08-31**, all **184 calendar dates**, timezone-aware timestamps at `+05:30`. |
| English and Romanized Hindi/Hinglish | PASS | Examples include `overnight buses do back to back honge? motion sickness hoti hai mujhe` and `that reel starts from Mumbai, hum Indore mein hain`. Generation/variety checks pass. |
| Typos and messy spelling | PASS | `nhi`, `thnks` and other fixed spelling variants are generated and tested. |
| One-word and short replies | PASS | **396 whitespace-single-token messages**, including `haan`, `done`, `ok` and emoji-only replies. |
| Emojis, interruptions and casual/college topics | PASS | Corpus tests and reviewed episodes cover emojis, assignments, exams, coding, movies, food, travel, events and unrelated interruptions. |
| Forwarded text and URLs | PASS | **44 forwarded messages** and **51 URL messages**. Forwarded wording is retained; URLs are fictional/example links. |
| Media placeholders | PASS | **134 image**, **24 PDF** and **57 voice** records, with `[Image]`, `[PDF]` and `[Voice message]` markers. These are placeholders, not fetched attachments. |
| At least 3 long decision threads | PASS | `TRIP_MANALI`, `HACKATHON_STACK`, `BIRTHDAY_EVENT`: **72 messages each**, six dated episodes each, rejected alternatives, interruptions and follow-up. |
| Threads reach concrete conclusions | PASS | `MSG_000713`: Manali, June 10–15, Rs 8,700 cap. `MSG_001482`: React/Vite/JavaScript + FastAPI/Python + SQLite. `MSG_003616`: July 25 at Nukkad Cafe, Rs 2,900 total. |
| Required fields, unique stable IDs and metadata | PASS | Required fields validate; IDs are unique and stable from `MSG_000001` to `MSG_004634`. Metadata records participants, counts, boundaries and decision threads. |
| Deterministic seed and reference date | PASS | Seed **20260901**, generator **1.0.0**, fixed reference **2026-09-01**. Both regenerated files match committed bytes. |
| Realism beyond the minimum varieties | WARNING | Background chat uses **56 recurring templates**. Repetition and simplified student routines limit ecological realism; no claim is made that this represents real-chat diversity. |

Corpus SHA-256: `d676b0a4872d627fa3a13b8d9ab7e8b87733b3e5dccff5efd914143a9a949371`. Supporting review: [backend/data/CORPUS_REVIEW.md](backend/data/CORPUS_REVIEW.md).

## Evaluation

| Requirement | Status | Evidence |
| --- | --- | --- |
| Exactly 40 labelled queries | PASS | `evaluation/queries.json` validates as **40** records with real target IDs, categories, flags and rationales. |
| Semantic, person and time categories | PASS | **20 semantic / 10 person / 10 time** queries; all three decision threads are covered. |
| At least 8 genuine zero-word-overlap queries | PASS | **10**, Q001–Q010. All query/target content-token intersections are empty under the unchanged convention. All ten semantic relationships were reviewed again; these are substantive paraphrases, not merely spelling or inflection tricks. |
| Overlap convention documented before scoring | PASS | `OVERLAP.md`, `overlap_convention.json`, the hard-subset review and freeze manifest establish the versioned convention and pre-scoring provenance. |
| Manual hard-subset review | PASS | `HARD_SUBSET_REVIEW.md` explains every pair and its distractors; this audit rechecked all ten original targets. |
| Independent human label review and representative coverage | WARNING | Labels were manually composed/reviewed by the authoring assistant, not an independent human annotator. All hard cases are semantic decision-thread queries; there are **37 distinct targets**, not 40 independent facts. Q001 has some acknowledged underspecification. No target was demonstrably invalid. |
| Overall Top-1 reported | PASS | Fresh all-method evaluation completed; hybrid **22/40 (55%)**. |
| Hard-subset accuracy separately reported with true denominator | PASS | Label is **Hard-10**, not Hard-8. Hybrid **1/10 (10%)**. |
| Signed overall–hard gap, including counts | PASS | Hybrid **55% (22/40) − 10% (1/10) = +45 percentage points**. All methods report the same measure. |
| Recall@3 and category breakdown | PASS | Generated JSON, CSV, terminal table and summary include all requested metrics; table below records the measured values. |
| No fabricated benchmark numbers | PASS | Recomputed aggregates from actual retrieved IDs. A second full run from freshly downloaded model files and fresh indexes reproduced **all four methods' rankings, full retrieved results and scores exactly**. Current/archived artifact hashes validate. |
| Frozen ground truth preserved | PASS | Freeze validation passes before/after scoring. Corpus, metadata, queries, overlap convention and expected IDs were not changed in this audit. |
| Labels excluded from ranking; no query-specific answer rules | PASS | Inspected retrieval inputs and source. Runtime receives query text/K and corpus data; no expected IDs, query categories, hard flags, label notes or conclusion/thread annotations determine ranking. |
| Comparison, debugging and artifacts | PASS | `--all` refreshes all four JSON reports, `comparison.json`, `comparison.csv`, `benchmark.png`, `evaluation_summary.md` and full failed-query diagnostics. |
| Honest failure/tuning record | PASS | `failure_analysis.md` covers all 19 initial errors; `tuning_notes.md` records the rejected experiment and retained general type filter. **18 hybrid Top-1 errors remain.** |
| Generalization and difficult semantic quality | WARNING | Same 40 queries were used for development/tuning. Hard accuracy remains **1/10**, despite overall gains. There is no held-out estimate and no minimum accuracy threshold was invented for this audit. |

Manual hard-query semantic checks: Q001 seaside/Goa and unaffordable/over cap; Q002 nausea/motion sickness; Q003 call off/cancel for unsafe roads; Q004 software/emulator on the judging laptop; Q005 accessibility/text alongside green; Q006 dorm lounge/hostel visitor restriction; Q007 abandoned picnic/dropping the lawn; Q008 alley game/bowling versus talking; Q009 unforeseen expenses/emergency buffer; Q010 misleading clip/reel departure-city mismatch. Context resolves references, while each labelled current message carries the requested information.

### Actual measured results

| Method | Top-1 | Recall@3 | Hard-10 Top-1 | Person | Time | Semantic | Gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Lexical | 9/40 (22.5%) | 16/40 (40%) | 0/10 (0%) | 3/10 (30%) | 3/10 (30%) | 3/20 (15%) | +22.5 pp |
| Semantic | 13/40 (32.5%) | 16/40 (40%) | 1/10 (10%) | 3/10 (30%) | 4/10 (40%) | 6/20 (30%) | +22.5 pp |
| Contextual | 4/40 (10%) | 12/40 (30%) | 1/10 (10%) | 1/10 (10%) | 2/10 (20%) | 1/20 (5%) | 0 pp |
| Hybrid | 22/40 (55%) | 25/40 (62.5%) | 1/10 (10%) | 7/10 (70%) | 8/10 (80%) | 7/20 (35%) | +45 pp |

Remaining hybrid errors: **Q001, Q002, Q003, Q004, Q005, Q007, Q008, Q009, Q010, Q011, Q012, Q015, Q016, Q022, Q023, Q027, Q031, Q032**. Q015 still selects a question instead of its answer; final-decision and difficult paraphrase failures remain. Returning a neighbor that contains the answer does not earn credit.

## Search and application behavior

| Requirement | Status | Evidence |
| --- | --- | --- |
| Meaning-based local retrieval | PASS | Pinned `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, NumPy cosine ranking, separate original/contextual representations and actual measured semantic baselines. |
| Lexical TF-IDF and typo tolerance | PASS | Word unigrams/bigrams plus character 3–5-grams; independent typo fixture passes. |
| Metadata-aware hybrid ranking and visible configuration | PASS | General weights and routing in `ranking_config.py`; author/date/type constraints filter the current message. Raw query supplies similarity channels. No new tuning in this audit. |
| Person searches | PASS | Explicit English/Hinglish sender requests enforce author filtering. Independent tests and a fresh real-model request for `Ishita ne budget pe kya bola?` confirm the correct author constraint. |
| Time searches | PASS | Corpus reference date, not system date, resolves relative time; date ranges, month/day qualifiers and event-date safeguards are tested. Fresh API queries for last month return August messages. |
| Actual message plus surrounding conversation | PASS | Original IDs/text are preserved. Embedding context is at most two neighbors per side; display context at most three, within 30 minutes and in chronological order. Tests and real-model API checks verify current-message identity and ordering. |
| Short replies | PASS | Real-model tests cover `done`, `haan pakka`, `this one`, `ok final`, distinguishing their contextual representations while preserving originals. This verifies representation behavior, not guaranteed correct answers. |
| Hinglish handling quality | WARNING | Code-mixed text is indexed unchanged, multilingual embeddings run locally, and Hinglish metadata grammar works. Strong semantic performance on varied Hinglish paraphrases has not been established; hard-query and exact-answer failures remain. |
| Health/search/stats API contracts | PASS | FastAPI routes and validation pass tests. Fresh real-model ASGI health/stats/search checks pass, including original text, ranks, metadata constraints and context. |
| No per-request document embeddings | PASS | Fresh real-model API test encoded exactly three query strings across three searches; document-cache checksums and modification times stayed unchanged. Startup shares the model/index; missing-model 503 behavior is tested. |
| React + Vite, JavaScript, plain responsive CSS | PASS | Source and dependency review confirms the requested stack and no unnecessary component library; production build succeeds. |
| Real APIs, interpretation, context expansion and UI states | PASS | Implementation and 22 frontend tests cover real relative API requests, original-message rendering, metadata, loading/error/empty handling, safe text rendering and dynamic stats. |
| Browser interaction and narrow/wide viewport acceptance | WARNING | Browser inventory returned no available browsers/apps. Actual clicks, Enter submission and visual mobile/desktop layout could not be checked interactively. Render tests/build are not presented as equivalent to browser verification. |

## Engineering and reproducibility

| Requirement | Status | Evidence |
| --- | --- | --- |
| Clean backend install | PASS | Created an isolated tracked-source copy with an empty venv, installed `requirements.lock.txt`; all **58 locked packages** match exactly (excluding bootstrap pip/setuptools/wheel), and `pip check` passes. Existing site-packages were not copied. Package download caches were allowed. |
| First-time model preparation and indexing | PASS | Downloaded the pinned public model into the isolated copy from scratch; built both original/contextual indexes from an empty embedding cache; full evaluation succeeds and matches existing results exactly. |
| Clean frontend install/build | PASS | Empty `node_modules`, `npm ci` from the lockfile, production build and all 22 tests pass in the isolated copy. npm reported **0 vulnerabilities** at install time; this is not a full security certification. |
| Backend test suite | PASS | **206 passed, none skipped**, both existing and freshly installed environments, including local real-model tests. |
| Evaluation tests | PASS | **40 passed** in the main environment; upstream warnings are recorded below. |
| Frontend production build and tests | PASS | `npm.cmd run build` and **22 tests** pass in both existing and fresh environments. |
| Exact benchmark reproduction | PASS | Fresh-install and existing evaluations have identical metrics, all top-three IDs, returned messages and score components for every method/query. |
| Reproducible README | PASS | Setup, generation, model preparation, startup/index caching, services, testing, evaluation and limitations are documented and exercised. Corrected the tested Python selection and stale introductory wording. |
| Cross-platform/newer-Python compatibility | WARNING | Clean installation verified only on **Windows, Python 3.9.10, Node 24.8.0, npm 11.6.0**. Other interpreters/platforms are unverified. README now states this rather than claiming every newer Python is supported. |
| No absolute machine paths in versioned files | PASS | Found one absolute output-directory path in an archived console log; converted the log from UTF-16 to UTF-8 and replaced that path with an explicitly redacted relative path. Post-fix tracked-text scan found none. Ignored local venv/cache files naturally contain local paths. |
| No secrets/credentials | PASS | No high-confidence credential patterns or assigned long credential strings found in tracked files; no credential files tracked. Reachable non-results source history also has no scanned high-confidence key patterns. This is a bounded heuristic scan, not proof against every possible secret format. |
| No private chat data | PASS | Committed data exactly matches independently regenerated fictional source templates, including metadata. No real-chat input, account connector or private-data dependency was used. |
| Correct `.gitignore` | PASS | Environments, node_modules, builds, caches, local logs, `.env` files and key files are ignored. `git ls-files -ci --exclude-standard` reports no tracked ignored artifacts. Lockfiles, labels, corpus and measured reports remain versioned. |
| Cache/artifact handling | PASS | Model/index caches are ignored, content/configuration keyed and integrity checked. Download/cache preparation is outside request handling. Synthetic data and small measured artifacts are intentionally retained for review. |
| Portable archived benchmark hashes | PASS | Found missing LF rules for nested `results/tuning/` files; added recursive result-artifact rules to `.gitattributes`. `git check-attr` confirms LF for archived JSON and patches. Existing archived comparison/artifact hashes still validate. |
| Modular responsibilities and no unnecessary rewrite | PASS | Corpus, parser, constraints, retrieval, service/context, schemas, API, React components and evaluation remain separate. No search/ranking algorithm changed during this audit. |
| Dependency/model/seed provenance | PASS | Direct and complete dependency pins, package-lock, fixed model revision/file hashes, CPU/token settings, seed/version, frozen inputs and source hashes are recorded. Model revision: `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`. |
| No external LLM API in normal execution | PASS | Initial public package/model downloads are required; normal encoding/inference is local with `local_files_only=True` and remote model code disabled. |
| Required scope and honest phase status | PASS | Implementation was authorized by subsequent tasks; the initial documentation-only instruction does not block those phases. No unmet browser acceptance or weak accuracy is marked complete or hidden. |

## Commands actually run

Commands below use the selected environment's Python; backend commands ran from `backend/`, evaluation commands from the repository root, and npm commands from `frontend/`. The clean copy used its own fresh interpreter and node_modules.

| Command/check | Outcome |
| --- | --- |
| `python -m pytest -q` (backend) | PASS: 206 tests in each environment. |
| `python -m pytest evaluation/tests -q` | PASS: 40 tests. |
| `python evaluation/evaluate.py --all` | PASS: all four methods in both environments, fresh indexes in the isolated copy. |
| `npm.cmd run build` | PASS after sandbox retry; also PASS after fresh `npm ci`. |
| `npm.cmd test` | PASS: 22 tests in each environment. |
| `python -m venv .venv`; `python -m pip install -r requirements.lock.txt`; `python -m pip check` | PASS in the isolated install. |
| `npm.cmd ci` | PASS in the isolated install. |
| `python -m scripts.prepare_model` | PASS: first-time public model download in the isolated install. |
| `python -m scripts.generate_data --output-dir ../.cache/reproduced`; `python -m scripts.validate_data --data-dir ../.cache/reproduced` | PASS: generated data and metadata match committed bytes. |
| Frozen-input validation, metric recomputation, artifact hashes, package-set comparison, path/credential scans and Git ignore/attribute checks | PASS within the scopes described above. |
| Fresh real-model ASGI health/stats/search and cache-reuse checks | PASS; this is an API smoke test, not a browser interaction test. |

**268 distinct tests passed** across backend, evaluation and frontend suites; repeated clean-install executions are not counted as additional distinct tests.

## Failures, warnings and fixes recorded

1. **Initial FAIL, resolved:** the sandbox denied Vite's temporary-config write (`EPERM`). Re-running the unchanged build with normal workspace access passed; fresh install/build also passed. This was an execution-permission issue, not a code fix.
2. **Initial FAIL, fixed:** the archived revert log contained one absolute machine path and was UTF-16. Its output path was explicitly redacted, and encoding normalized. Scores, queries and outcomes were not changed.
3. **Initial WARNING, fixed:** nested benchmark archives had no explicit line-ending policy. Recursive LF rules now protect their hashes across future checkouts.
4. **Documentation corrected:** introductory future-tense wording and an overbroad Python compatibility claim were replaced with implemented behavior and the tested interpreter. Historical phase measurements remain labelled as history.
5. **Nonblocking upstream warnings:** matplotlib/pyparsing emitted 14 deprecation warnings in evaluation tests. The tokenizer printed its packaged 128-token length warning while contextual input length was counted; the encoder uses the documented 256-token limit, and fresh inference/tests completed. No warning was suppressed or recast as a test failure.
6. **Audit probe error, corrected:** a read-only diagnostic initially imported a nonexistent unused overlap helper. The corrected probe and frozen validator passed; no application change was needed.
7. **Outstanding WARNINGS:** limited hard-query quality, development-set tuning, repeated synthetic templates, lack of independent human label review, unverified other platforms, and unavailable browser interaction checks. Further ranking tuning was intentionally not performed during readiness auditing.

No unresolved observed implementation **FAIL** remains. The browser acceptance item in PLAN.md remains open. Supporting measurements and all failures are retained in `results/`; ignored clean-install scratch data is not part of the submission.
