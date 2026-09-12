# IT Geeks assessment review

## Follow-up implementation update (2026-09-12)

The authorized improvement adds a pinned local multilingual reranker to the API and hybrid evaluation. Current Top-1 is **25/40 (62.5%)**, Recall@3 **29/40 (72.5%)**, and hard Top-1 remains **1/10 (10%)**: the gap is now **52.5 percentage points**. Person improves 7/10 → 10/10, semantic 7/20 → 8/20, and time regresses 8/10 → 7/10. Fifteen assessment queries still fail.

Separately frozen English/Hinglish pairs now provide end-to-end language measurements: 8/24 → 17/24 overall, including Hinglish 3/12 → 7/12. This is small supplemental development evidence, not independent held-out validation. The original 40 queries and corpus are unchanged. Broad queries now incur several seconds of pairwise inference, and setup requires a second local model.

All 232 backend, 42 evaluation and 22 frontend tests pass, as does the production build. The full four-method benchmark was rerun. See [tuning_notes.md](results/tuning_notes.md) for candidate recall, exact gains/losses, latency, setup issues and the stop decision. The README describes current behavior and both model-preparation commands. Browser verification and a fresh installation of this new two-model version remain outstanding.

The review below records the preceding submission and the findings that motivated this work; its metrics and unmeasured-Hinglish statements are historical.

Reviewed 2026-09-12 against `AGENTS.md`, `PLAN.md`, the implementation, frozen corpus/labels, saved tuning history, API/frontend code, dependency configuration and audit evidence. Initial inspection and live retrieval probes preceded changes. This is a technical review, not an official assessment grade.

**Verdict: the submission satisfies the core structural requirements and has strong reproducibility evidence on Windows, but semantic answer selection is its main weakness. Browser acceptance checks remain incomplete.** No minimum accuracy is specified in `AGENTS.md`; poor measured accuracy must still be disclosed.

## 1. Strongest parts

- The deterministic, synthetic-only corpus contains 4,634 messages, exactly eight fictional participants and all 184 dates from March through August 2026. It includes Hinglish, typos, short/emoji-only replies, forwards, URLs and media placeholders. Three 72-message decision threads reach concrete conclusions and contain interruptions and rejected alternatives.
- Retrieval, query parsing, metadata constraints, context assembly, API schemas and UI components have separate responsibilities. Local multilingual embeddings and word/character TF-IDF are real implementations.
- Results preserve the actual central message ID, text, sender and timestamp. Embedding context is bounded to two neighbors per side within 30 minutes; display context allows three per side. A nearby answer does not count as a correct target in evaluation.
- Frozen input hashes, a documented overlap convention, per-query results, model revision, dependency locks and visible ranking weights make results inspectable. Failures and rejected tuning experiments are retained.
- The API initializes one search engine per process. Document embeddings are cached; requests encode the query, not the corpus. The frontend uses the real APIs and implements loading, empty, error and cancellation behavior.

## 2. Missed requirements and incomplete evidence

**PASS:** The numerical corpus and evaluation requirements, three concrete decision threads, local semantic retrieval, lexical baseline, person/time retrieval, original-message context, measured overall/hard accuracy and gap are implemented. Frozen validation passes: 40 queries, 10 hard queries, all three categories and existing targets.

**WARNING:** `PLAN.md` explicitly requires narrow/wide-screen UI acceptance checks. Browser interaction and visual checks remain unverified; build/render tests do not establish these. The demo-video URL is still a placeholder. Supply it if the submission process requires a video.

**WARNING:** All 40 queries are English; there is no separately measured end-to-end Hinglish query subset. No independent held-out set exists. These are quality/evidence gaps, not grounds to invent an accuracy threshold or relabel targets.

**WARNING:** The documented hard-subset review was performed by the authoring assistant, not an independent human annotator. The manually composed labels should not be presented as independently human-validated ground truth.

## 3. Likely live-demo failures

Actual read-only probes before the fix produced these first hits:

| Query | Retrieved original message | Assessment |
| --- | --- | --- |
| When did we decide on Manali? | `MSG_000296`: “Manali stay mein hot water included hai, heater extra” | Related detail, not the final decision |
| Which backend did we finally pick? | `MSG_001293`: “Yes, but pick after testing a clean laptop launch” | Earlier proposal rather than chosen stack |
| What did we discuss last month? | `MSG_004243`: “ask our tutor, don't assume based on last week” | Correct August constraint, generic answer; the broad query has no unique answer |
| Rohan ne project ka naam kya suggest kiya? | `MSG_000882`: a masala-dosa/mess-menu message | Correct author but unrelated meaning |
| Ishita ne pichle mahine budget pe kya bola? | `MSG_003945`: “owe you chole kulche 😅” | Correct author/month but unrelated meaning |
| What restriction prevented the birthday gathering from using the dorm lounge? | `MSG_003418`: “Hostel common room can't allow outside students after 6 that day” | Correct hard-query target, Q006 |

These are retrieval-quality failures, not API crashes. No ranking changes or example-chip substitutions were made to conceal them.

A corrupt model manifest containing valid JSON such as `{}` caused an uncaught `KeyError` during initialization. **Fixed:** shared schema validation now raises the controlled setup error before loading the model. Regression tests verify health/stats remain accessible and search responds with HTTP 503 and preparation instructions. This does not repair a damaged cache automatically.

The first benchmark attempt during this review failed with `MemoryError` while loading the tokenizer alongside other checks. A sequential rerun passed. Resource contention is a plausible explanation, not a measured minimum-RAM result. Avoid running multiple model-heavy processes on a constrained demo machine.

The tokenizer also emits a 129-versus-128 length warning. Inference is explicitly configured for 256 tokens; the complete run finishes without an indexing exception. The warning remains visible. Missing model files require preparation before search, and a successful health response alone does not prove search readiness.

## 4. README discrepancies

The following factual discrepancies were corrected locally, preserving the document's organization:

- The API example had invalid JSON and nonexistent `query_metadata`/nested `scores` fields at the indicated locations. It now describes the actual schema and links to captured real JSON.
- “Last week” was documented as August 25–31; the implementation uses the previous complete Monday–Sunday week, August 24–30. The unsupported `pichle month` example was replaced with `pichle mahine`.
- Semantic retrieval misses **27**, not 22, of the 40 targets.
- Frontend tests use Node's built-in runner, not Vitest. Exact frontend versions and verified runtime versions replace broad claims.
- An illustrative context example used a real-looking corpus ID without identifying it as invented. It is now explicitly illustrative with an `EXAMPLE_REPLY` identifier.
- Cache invalidation uses encoded text and encoder settings rather than the raw corpus file hash alone. Comparison artifacts do not contain the full per-method rankings.
- Overlap tokenization retains words inside URLs, and the Q001 token example omitted `made`.
- Unqualified Hinglish claims, the one-GB setup estimate, a few nonexistent tree entries, stale current test counts and the implication that setup commands activate the environment were corrected.

Historical phase/test counts in `PLAN.md` and `FINAL_AUDIT.md` describe earlier runs and were not rewritten as current evidence.

## 5. Evaluation leakage and overfitting

No direct answer leakage was found in retrieval code: expected IDs, query IDs, evaluation categories and authoring decision labels are not ranking inputs. Corpus metadata supplies legitimate participant/date information; the semantic representations do not ingest expected answers. Frozen corpus, labels and overlap files still validate unchanged.

There is **development-set selection bias**: the same 40 queries informed weight selection and the later general message-type improvement. The historical experiments are visible, and the retained rule handles a class of explicit requests rather than a single query. Nevertheless, 55% is a development-set result, not independent generalization evidence.

There are only 37 distinct targets; each final decision is tested twice. All ten hard queries come from the three authored decision discussions. For future evaluation, collect independently labelled examples and split by thread/topic before choosing weights. Do not keep optimizing this small frozen set.

## 6. Are zero-word-overlap tests genuinely difficult?

Yes. All ten pass the frozen text-only content-token convention, and the relationships are meaningful paraphrases rather than spelling tricks. Examples include seaside holiday versus Goa; nausea/consecutive coach rides versus motion sickness/back-to-back buses; and dorm lounge versus hostel common room. Negation and substantive quantities remain tokens.

The selected Q006 is a valid answer-bearing target and the only hard query hybrid gets right. Hard Top-1 is **1/10 (10%)**. Context and metadata can still share clues with the query: zero overlap is defined against the original target text, not every retrieval input. These cases are difficult but narrow; they do not independently test hard person/time queries. Q001 permits plausible earlier cost explanations, which is a single-target-label limitation rather than proof its chosen rejection message is invalid.

## 7. Is Hinglish a core use case?

It is a core **data and parser** use case: authored code-mixed messages, multilingual embeddings and English/Hinglish grammar tests are present. It is not yet a convincingly validated semantic-query use case. English queries targeting Hinglish messages are useful cross-language tests but do not replace Hinglish queries. The failed live probes above show that correct metadata parsing alone is insufficient. Add an independently labelled bilingual evaluation set in future work, preserving this benchmark.

## 8. Do person and time searches behave differently?

Yes. Explicit sender language such as `what did Ishita say` or `Rohan ne` filters the **current message's author**. A weaker person mention can receive only a bonus; a name used as a topic/recipient does not automatically filter. Dates resolve against corpus reference date **2026-09-01**, with no clock dependency. Chat-date constraints filter current-message timestamps; author/date/type constraints intersect. Empty intersections stay empty.

Observed eligible counts illustrate the difference: the Ishita budget query retained 596 of 4,634 messages; last month retained 745 August messages; the combined Ishita/August query retained 102. A hard constraint also shifts 0.10 ranking weight from contextual to original semantic similarity. Person Top-1 is **7/10 (70%)**, time **8/10 (80%)**, and semantic **7/20 (35%)**. These gains do not isolate each component causally, but source inspection confirms distinct behavior.

## 9. Clean-machine reproducibility

The earlier clean-source audit in [FINAL_AUDIT.md](FINAL_AUDIT.md) and [audit_evidence.json](results/audit_evidence.json) records a fresh Windows virtual environment, locked Python/frontend dependencies, a fresh public-model download, fresh indexes, byte-identical corpus regeneration and matching benchmarks. Verified versions are Python 3.9.10, Node 24.8.0 and npm 11.6.0. No secrets or private chat are needed; generated model/index/install artifacts are ignored sensibly.

This review reused the installed environment, reran dependency consistency, frozen-input validation, all tests, the production build and the full benchmark after the fix. It did not repeat a fresh installation or verify Linux/macOS. Their commands are provided, but platform-specific dependencies and numeric behavior remain unverified. Initial dependency/model setup needs network access; normal model inference is local. Several GB of disk space should be reserved, and minimum RAM has not been established.

## 10. Five likely interviewer questions

1. Why does contextual-only retrieval score 10% while original-only embeddings score 32.5%, and how do you prevent a neighboring answer from receiving credit for the current message?
2. What does the 45-percentage-point overall-versus-hard gap tell you? How would you design a held-out evaluation given that these queries informed tuning and contain repeated targets?
3. Walk through an English or Hinglish person-plus-time query: when do you filter, when do you boost, how are dates resolved, and what happens when no message satisfies the intersection?
4. What enters each embedding/cache key, when are document vectors rebuilt, and how do model pinning, file checksums and initialization errors affect a clean-machine demo?
5. Why are zero-overlap cases meaningful under your convention, what information may still overlap through metadata/context, and how would you measure Hinglish-query quality separately?

## Changes and verification

Runtime edits are limited to model-manifest validation in `backend/app/search/model_config.py`, its use in `embedding.py` and `scripts/prepare_model.py`, plus ten regression tests in `backend/tests/test_model_manifest.py`. README corrections and this review document the findings. Benchmark artifacts were regenerated; no corpus, label, model, ranking weight or frontend behavior changed.

| Check | Command | Result |
| --- | --- | --- |
| Backend (from `backend/`) | `.\.venv\Scripts\python.exe -m pytest -q` | 216 passed |
| Evaluation tests (root) | `.\backend\.venv\Scripts\python.exe -m pytest evaluation/tests -q` | 40 passed; 14 pyparsing deprecation warnings |
| Frontend (from `frontend/`) | `npm.cmd test` | 22 passed |
| Production build (from `frontend/`) | `npm.cmd run build` | Passed |
| Complete evaluation (root) | `.\backend\.venv\Scripts\python.exe evaluation/evaluate.py --all` | Sequential rerun passed; initial concurrent run failed as described above |
| Frozen inputs (root) | `.\backend\.venv\Scripts\python.exe -m evaluation.validate_queries` | Passed; freeze verified |
| Dependencies (root) | `.\backend\.venv\Scripts\python.exe -m pip check` | No broken requirements |

An initial attempt to execute `evaluation/validate_queries.py` directly failed on relative imports; its supported package invocation above passed. This was a review-command error, not a changed implementation requirement.

| Method | Top-1 | Recall@3 | Hard-10 Top-1 | Overall minus hard |
| --- | --- | --- | --- | --- |
| Lexical | 9/40 (22.5%) | 16/40 (40%) | 0/10 (0%) | +22.5 pp |
| Semantic | 13/40 (32.5%) | 16/40 (40%) | 1/10 (10%) | +22.5 pp |
| Contextual | 4/40 (10%) | 12/40 (30%) | 1/10 (10%) | 0 pp |
| Hybrid | 22/40 (55%) | 25/40 (62.5%) | 1/10 (10%) | +45 pp |

All measured scores and retrieved rankings remain unchanged by the fix. Current per-query failures and scores are in [failed_queries.txt](results/failed_queries.txt); [failure_analysis.md](results/failure_analysis.md) explains the initial failures and identifies the 18 that remain. Further retrieval tuning was outside this critical-fix review.
