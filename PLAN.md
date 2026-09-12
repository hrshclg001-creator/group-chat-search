# Implementation plan

Status: RecallChat's React search interface, corpus generation, frozen evaluation labels, lexical/semantic/contextual baselines, deterministic query parsing, metadata-aware hybrid retrieval and search/stats APIs are implemented. The corpus contains 4,634 messages and the evaluation set has 40 queries, including 10 hard cases. Measured Top-1 is lexical 9/40, original-only semantic 13/40, contextual 4/40 and hybrid 22/40 after general message-type filtering; artifacts are under `results/`. Hybrid weights were selected from four profiles on these same queries, so its result is not held-out accuracy. The UI uses real APIs and shows original matching messages with expandable context. Fresh Windows installation and evaluation from an isolated tracked-source copy are verified in FINAL_AUDIT.md. Browser visual/interaction verification remains outstanding. Later work requires subsequent authorization.

Latest tuning phase: all 19 initial hybrid failures were reviewed before code changes. Metadata-text removal was measured and rejected (20/40); a full revert run restored 21/40. General current-message type constraints then improved Top-1 to 22/40 (55%), Recall@3 stayed 25/40, hard Top-1 stayed 1/10 (10%), and the gap is +45 pp. Time accuracy is 8/10; person 7/10 and semantic 7/20 are unchanged. All three baseline rankings and frozen inputs are unchanged. `results/failure_analysis.md` and `results/tuning_notes.md` record evidence, archived trials and the decision to stop before further evaluation-set fitting. All 206 backend tests and 40 evaluation tests passed. Earlier phase measurements below remain historical.

Assessment-readiness audit: [FINAL_AUDIT.md](FINAL_AUDIT.md) checks every requirement and records PASS/WARNING/initial resolved FAIL findings. All 206 backend, 40 evaluation and 22 frontend tests pass; the fresh installation also passes backend/frontend checks and reproduces every benchmark ranking/score after first-time model download and indexing. Corpus and metadata regenerate byte-for-byte. Only archive path/encoding, archived-artifact line endings and stale setup documentation needed correction. No retrieval algorithm or frozen input changed. Browser inventory was empty, so Phase 5 interactive viewport checks remain open; cross-platform installation is not claimed.

## Architecture

1. A deterministic Python generator writes a synthetic JSONL corpus and participant metadata using a fixed seed. Messages have stable IDs, participant IDs, timezone-aware timestamps, text, and optional thread/media/forward markers.
2. A separate, manually authored JSON evaluation array at `evaluation/queries.json` stores query ID, text, category, expected message ID, hard-subset membership, and a labelling rationale. This follows the subsequently requested JSON format rather than the originally proposed JSONL. Labels never enter the retrieval pipeline.
3. An indexing module validates the corpus, builds lexical TF-IDF features, and computes local `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` embeddings. Cache artifacts are keyed by corpus hash, model revision, and indexing configuration.
4. Independent lexical and semantic baselines rank messages. Semantic ranking uses NumPy cosine similarity with documented normalization and stable tie-breaking. A hybrid ranker combines normalized signals with person/time metadata boosts or filters. Document ambiguous name and date handling.
5. Context assembly adds a bounded window of nearby messages to each hit. It retains the actual matching message ID, text, author, timestamp, and score, with surrounding messages in chronological order. Context does not replace the selected hit or count as a correct hit during evaluation.
6. FastAPI validates requests, loads prepared indexes, and returns structured search hits with context and actionable errors.
7. React with Vite and plain responsive CSS provides search input, clearly identified matching messages, author/time details, context, and loading/empty/error states.
8. Independent Python evaluation scripts compare all three retrieval modes using identical inputs and save per-query outputs and aggregate metrics.

## Proposed folder structure

This is a future architecture layout. Subsequent authorized tasks use `backend/requirements.txt`, `backend/scripts/`, `backend/data/messages.jsonl`, `backend/data/corpus_metadata.json`, and `results/`; other modules below remain planned. README.md documents the current implemented paths.

```text
AGENTS.md
PLAN.md
README.md
.gitignore
data/
  corpus/messages.jsonl
  corpus/participants.jsonl
  evaluation/queries.jsonl
  evaluation/label_changes.md
  manifests/generation.json
backend/
  pyproject.toml
  app/
    main.py
    api/search.py
    schemas.py
    config.py
    data/loader.py
    retrieval/
      lexical.py
      semantic.py
      metadata.py
      hybrid.py
      context.py
      index.py
  tests/
scripts/
  generate_data.py
  validate_data.py
  build_index.py
  evaluate.py
evaluation/
  metrics.py
  overlap.py
  tests/
frontend/
  package.json
  src/
    App.jsx
    components/
    api/
    styles.css
  tests/
artifacts/                  # Ignored generated indexes and model caches
reports/                    # Measured results and reproducibility notes
```

## Phases and acceptance criteria

### Phase 0: Planning documents (completed)

Create only AGENTS.md, PLAN.md, a short README.md overview, and .gitignore. Preserve mandatory requirements and engineering rules without scaffolding or implementing the application.

Acceptance: only the four requested files are created or updated; requirements, architecture, future folder structure, and acceptance criteria are documented.

### Phase 1: Project foundations and data contracts

Scaffolding, corpus and evaluation-query validation, seed/timestamp conventions, deterministic generation checks, pinned local model configuration/preparation, and validated search/stats API schemas are implemented. Health/CORS and API tests accompany the backend; prior frontend scaffold checks are recorded in README. Search schemas enforce a nonblank query of up to 2,000 characters and integer top_k from 1 to 50, with explicit original-message, context, score, metadata and rank response fields.

Establish modular Python/FastAPI and React/Vite foundations with plain responsive CSS. Define participant, message, evaluation-query, search-request, and search-response schemas. Establish the fixed seed, timestamp conventions, configuration, dependency locking, model revision recording, and deterministic test fixtures.

Acceptance: schema tests reject malformed records; frontend build and backend smoke checks pass; runtime configuration requires no secrets or external LLM API. Run relevant tests and document commands.

### Phase 2: Synthetic corpus

Completed for the authorized dataset phase: 4,634 synthetic messages, exactly eight fictional participants, all 184 dates from March 1 through August 31, 2026, and fixed reference date September 1, 2026. Three hand-authored decision threads each have 72 messages across six dates, with recorded conclusion IDs and intervening chatter. Generator and validator passed; 32 backend tests passed, including independent byte-for-byte regeneration. Generated samples and all three authored threads were reviewed; scope and template limitations are recorded in `backend/data/CORPUS_REVIEW.md`. No retrieval or evaluation implementation was added.

Design exactly 8 realistic fictional participants and generate at least 4,000 messages across approximately 6 months. Include coherent recurring topics, interruptions, realistic Hinglish/code-mixed language, typos, one-word replies, forwarded messages, media placeholders, emojis, and messy conversational text. Include at least 3 long decision threads with alternatives, discussion, and concrete conclusions. Record thread IDs, message ranges, and conclusion IDs for review. Persist JSONL and a manifest containing seed, date range, counts, generator version, and corpus hash.

Acceptance: validators confirm message count, exactly 8 participating authors, unique IDs, valid references, chronology, and the documented approximate six-month span. Manual review verifies realism, all required text forms, and 3 sustained decision threads with conclusions. Regenerating twice with the same configuration produces identical corpus bytes. No real/private chat is used. Run generator and validator tests.

### Phase 3: Manual evaluation set and ground-truth freeze

Completed: `evaluation/queries.json` contains 40 manually authored labels (20 semantic, 10 person, 10 time) referencing actual unchanged corpus messages. Q001-Q010 form the 10-case zero-overlap subset under the documented versioned convention; the authoring assistant reviewed their semantic connection and ambiguity in context. There are 37 distinct targets, with the three final decisions intentionally repeated under time constraints. `freeze_manifest.json` records corpus/query/convention/review hashes before retrieval or scoring, and `label_changes.md` records provenance and correction requirements. Validator passed with frozen integrity verified; 20 evaluation tests passed. No search engine or benchmark results were added.

Manually write and label exactly 40 queries against the fixed corpus with expected message IDs and rationales. Cover semantic meaning, person-based, and time-based searches, assigning a primary category for reporting. Include at least 8 queries with zero meaningful word overlap with their targets. Before scoring, document token normalization, punctuation/emoji handling, and stopword treatment, including Hinglish; do not invent exclusions to force hard-subset membership. Review label correctness and ambiguity, manually review the hard subset, then freeze corpus/query hashes. Track subsequent legitimate corrections explicitly.

Acceptance: exactly 40 manually labelled queries reference existing targets, all 3 query categories are represented, and at least 8 reviewed hard queries satisfy the documented overlap convention. No answers have been changed to improve scores. Run query-schema, target-reference, and overlap validation tests.

### Phase 4: Retrieval and context

Core retrieval implemented: `backend/app/search/` provides lexical TF-IDF (fixed 0.7 word / 0.3 character cosine weights), original-only multilingual MiniLM embeddings, contextual embeddings using up to two previous and two following messages within 30 minutes, and hybrid retrieval with person/time constraints. Original target IDs and text remain intact, and neighbors never earn target credit. Local model revision/file hashes, normalized embeddings, stable ID ties, bounded token budgets, cache invalidation/checksums and offline model tests are implemented. Hybrid hits expose scores, constraints, ranking weights and original-target display context. The three baseline implementations remain unchanged; search API/UI integration belongs to Phase 5.

The standalone parser detects metadata names/calendar constraints using the corpus reference date, never the machine clock. Hybrid's separate constraint layer distinguishes explicit sender language from uncertain name mentions, intersects strong author/date filters, handles month/day parts and avoids interpreting event dates as chat dates. Empty intersections return no results. `ranking_config.py` contains all four measured weight profiles and routing thresholds; the selected balanced profile transfers 0.10 context weight to original-message similarity when hard constraints apply. No query/category/target IDs determine weights or answers. Latest checks: all 166 backend tests and 30 evaluation tests passed (196 total). README documents exact rules, limitations, weights and tuning provenance.

Implement TF-IDF and multilingual embedding baselines independently. Add NumPy cosine similarity, person/time handling, hybrid ranking, and bounded nearby-message context. Cache embeddings/indexes with invalidation checks and stable ranking tie-breaks. Document ranking weights and tuning provenance without feeding evaluation labels into retrieval or hand-coding answers.

Acceptance: each mode returns actual corpus messages with correct IDs and useful chronological context. Tests cover scoring, stable ties, empty queries, person/time handling, context boundaries, and stale cache detection using deterministic fixtures. Confirm local embedding inference after model preparation. Run relevant retrieval tests.

### Phase 5: Search API and frontend

API portion implemented: `POST /api/search` returns actual hybrid targets plus up to three previous/next messages within 30 minutes, chronological display context, scores, detected constraints, one-based ranks and measured search time. `GET /api/stats` returns loaded-corpus counts/date bounds and reference date/timezone. FastAPI initializes one service/model/index per process at startup; requests encode only the query and never rebuild document embeddings. Missing model/index initialization yields search HTTP 503 while health/stats remain accessible. CORS supports local React POST requests. API-phase checks passed: 191 backend tests and 30 evaluation tests (221 total); real HTTP checks verified endpoint behavior, unchanged document-cache hashes and parity with saved hybrid rankings. Examples preserve actual outputs, including the Manali query's unrelated movie hit.

Frontend portion implemented: RecallChat uses real search/stats APIs, Enter/button/chip submission, metadata badges, highlighted original chat messages with quieter expandable context, measured relevance/latency, dynamic corpus statistics and a transparent explanation panel. Plain responsive CSS includes small-screen layouts and reduced-motion support. Loading, empty, errors, retries, timeouts and request cancellation are implemented without new dependencies. All 22 frontend tests and the production build passed; live proxy requests returned the expected checklist message. Browser automation reported no available browsers, so visual mobile/desktop layout and click-through checks remain unverified. Phase 5's browser acceptance checks are still outstanding.

Expose validated search requests through FastAPI and integrate the React interface. Clearly display matching message, author, timestamp, and surrounding conversation. Support responsive layouts and loading, no-result, and error states.

Acceptance: end-to-end searches return the same hit IDs as direct retrieval, context remains associated with its hit, invalid requests produce clear errors, and the interface works on narrow and wide screens. Run API/frontend tests, a frontend production build, and integration checks.

### Phase 6: Evaluation and honest analysis

Unified reporting is implemented: `python evaluation/evaluate.py --all` reruns lexical, semantic, contextual and hybrid against the unchanged frozen inputs, shares the local encoder, and prints a count-labelled terminal table plus all failure details and score components. It generates four method JSON files, `comparison.json`, numeric `comparison.csv`, a matplotlib `benchmark.png`, complete `failed_queries.txt` and an automatically generated `evaluation_summary.md`. Hard-subset labels use the actual count (10), with numerators/denominators and signed overall-minus-hard gaps throughout. Existing single-method and saved-report comparison commands remain supported. The full run reproduced prior metrics without tuning or label changes. Latest checks: 40 evaluation tests, 191 backend tests and dependency checks passed; artifact/CSV/hash consistency and all 113 failure records were verified, and the chart was visually inspected.

All requested comparison methods are measured against identical frozen inputs. `python evaluation/evaluate.py --method` accepts lexical, semantic, contextual or hybrid and records metrics, rankings, configuration, environment and hashes. Lexical Top-1 is 9/40 (22.5%), Recall@3 16/40 (40%), hard Top-1 0/10 (0%), gap +22.5 pp. Original-only semantic Top-1 is 13/40 (32.5%), Recall@3 16/40 (40%), hard Top-1 1/10 (10%), gap +22.5 pp. Contextual Top-1 is 4/40 (10%), Recall@3 12/40 (30%), hard Top-1 1/10 (10%), gap 0 pp. Hybrid Top-1 is 21/40 (52.5%), Recall@3 25/40 (62.5%), hard Top-1 1/10 (10%), gap +42.5 pp; category Top-1 is semantic 7/20, person 7/10 and time 7/10. `python -m evaluation.compare --all` validates report/input integrity and writes `results/comparison.json` with every metric and query-level gains/losses. All 19 hybrid errors were printed and saved; no frozen input or expected answer changed.

The user explicitly authorized evaluation-driven hybrid weight selection. Four general profiles were declared and measured; balanced tied original_first on overall Top-1 and Recall@3 and won the declared-order tie-break. `results/hybrid_tuning.json` retains all trials and source/configuration hashes. A final rerun verified the same outcomes. No individual query IDs or category labels enter ranking, and no further failure-specific rules were added. These are tuning-set metrics rather than held-out accuracy; hard semantic performance remains poor. All backend/evaluation tests passed. The subsequent API task preserved retrieval and benchmark artifacts. Frontend search and clean-checkout delivery remain later phases.

Run lexical, semantic, and hybrid retrieval against the same frozen 40-query set and corpus. Report:

- Overall Top-1 accuracy: correct first-ranked message IDs divided by 40.
- Recall@3: queries whose labelled target appears in the first 3 hits divided by query count, since each query has one expected target.
- Top-1 accuracy by primary query category, with counts and denominators.
- Top-1 accuracy on the hard zero-overlap subset, with its actual count and denominator.
- Overall Top-1 minus hard-subset Top-1 in percentage points for each method, preserving the sign.

Save per-query ranked IDs, correctness, corpus/query hashes, model/dependency versions, and ranking configuration. Explain failures and limitations without fabricated numbers or hidden ground-truth changes.

Acceptance: all three methods have every requested metric and an explicit overall/hard-subset gap. Metric tests cover known rankings, misses, short result lists, and category/subset aggregation. Results can be recomputed from saved inputs. No minimum accuracy is invented and no result is claimed before measurement.

### Phase 7: Reproducible delivery

Expand README.md with prerequisites, exact installation/run commands, fixed seed, data generation, initial model download/cache behavior, indexing, backend/frontend startup, tests, and evaluation. Include measured comparison results or links to committed reports, document category/overlap conventions, and disclose limitations. Verify the workflow from a clean checkout.

Acceptance: a reviewer can reproduce the corpus, run search, execute tests, and regenerate reported metrics from README instructions without secrets or an external LLM API. Document observed platform or numeric reproducibility limits. Account for every mandatory requirement in AGENTS.md.
