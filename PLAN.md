# Implementation plan

Status: initial application scaffolding authorized and implemented: React/Vite frontend, FastAPI health endpoint, local CORS, and connection status. Phase 1 is only partially implemented; data contracts and reproducibility configuration remain future work. Corpus, retrieval, evaluation labels, and benchmark results have not been created. Later work requires subsequent authorization.

## Architecture

1. A deterministic Python generator writes a synthetic JSONL corpus and participant metadata using a fixed seed. Messages have stable IDs, participant IDs, timezone-aware timestamps, text, and optional thread/media/forward markers.
2. A separate, manually authored JSONL evaluation set stores query ID, text, category, expected message ID, hard-subset membership, and a labelling rationale. Labels never enter the retrieval pipeline.
3. An indexing module validates the corpus, builds lexical TF-IDF features, and computes local `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` embeddings. Cache artifacts are keyed by corpus hash, model revision, and indexing configuration.
4. Independent lexical and semantic baselines rank messages. Semantic ranking uses NumPy cosine similarity with documented normalization and stable tie-breaking. A hybrid ranker combines normalized signals with person/time metadata boosts or filters. Document ambiguous name and date handling.
5. Context assembly adds a bounded window of nearby messages to each hit. It retains the actual matching message ID, text, author, timestamp, and score, with surrounding messages in chronological order. Context does not replace the selected hit or count as a correct hit during evaluation.
6. FastAPI validates requests, loads prepared indexes, and returns structured search hits with context and actionable errors.
7. React with Vite and plain responsive CSS provides search input, clearly identified matching messages, author/time details, context, and loading/empty/error states.
8. Independent Python evaluation scripts compare all three retrieval modes using identical inputs and save per-query outputs and aggregate metrics.

## Proposed folder structure

This is a future layout. The initial scaffold uses `backend/requirements.txt`, `backend/scripts/`, `backend/data/`, and `results/` as subsequently requested; other modules below remain planned.

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

Initial scaffolding only is implemented. Health and CORS tests and frontend checks accompany it; see README.md for commands and validation. Data schemas, seed/timestamp conventions, model configuration, and deterministic corpus fixtures are not implemented, so the full phase remains incomplete.

Establish modular Python/FastAPI and React/Vite foundations with plain responsive CSS. Define participant, message, evaluation-query, search-request, and search-response schemas. Establish the fixed seed, timestamp conventions, configuration, dependency locking, model revision recording, and deterministic test fixtures.

Acceptance: schema tests reject malformed records; frontend build and backend smoke checks pass; runtime configuration requires no secrets or external LLM API. Run relevant tests and document commands.

### Phase 2: Synthetic corpus

Design exactly 8 realistic fictional participants and generate at least 4,000 messages across approximately 6 months. Include coherent recurring topics, interruptions, realistic Hinglish/code-mixed language, typos, one-word replies, forwarded messages, media placeholders, emojis, and messy conversational text. Include at least 3 long decision threads with alternatives, discussion, and concrete conclusions. Record thread IDs, message ranges, and conclusion IDs for review. Persist JSONL and a manifest containing seed, date range, counts, generator version, and corpus hash.

Acceptance: validators confirm message count, exactly 8 participating authors, unique IDs, valid references, chronology, and the documented approximate six-month span. Manual review verifies realism, all required text forms, and 3 sustained decision threads with conclusions. Regenerating twice with the same configuration produces identical corpus bytes. No real/private chat is used. Run generator and validator tests.

### Phase 3: Manual evaluation set and ground-truth freeze

Manually write and label exactly 40 queries against the fixed corpus with expected message IDs and rationales. Cover semantic meaning, person-based, and time-based searches, assigning a primary category for reporting. Include at least 8 queries with zero meaningful word overlap with their targets. Before scoring, document token normalization, punctuation/emoji handling, and stopword treatment, including Hinglish; do not invent exclusions to force hard-subset membership. Review label correctness and ambiguity, manually review the hard subset, then freeze corpus/query hashes. Track subsequent legitimate corrections explicitly.

Acceptance: exactly 40 manually labelled queries reference existing targets, all 3 query categories are represented, and at least 8 reviewed hard queries satisfy the documented overlap convention. No answers have been changed to improve scores. Run query-schema, target-reference, and overlap validation tests.

### Phase 4: Retrieval and context

Implement TF-IDF and multilingual embedding baselines independently. Add NumPy cosine similarity, person/time handling, hybrid ranking, and bounded nearby-message context. Cache embeddings/indexes with invalidation checks and stable ranking tie-breaks. Document ranking weights and tuning provenance without feeding evaluation labels into retrieval or hand-coding answers.

Acceptance: each mode returns actual corpus messages with correct IDs and useful chronological context. Tests cover scoring, stable ties, empty queries, person/time handling, context boundaries, and stale cache detection using deterministic fixtures. Confirm local embedding inference after model preparation. Run relevant retrieval tests.

### Phase 5: Search API and frontend

Expose validated search requests through FastAPI and integrate the React interface. Clearly display matching message, author, timestamp, and surrounding conversation. Support responsive layouts and loading, no-result, and error states.

Acceptance: end-to-end searches return the same hit IDs as direct retrieval, context remains associated with its hit, invalid requests produce clear errors, and the interface works on narrow and wide screens. Run API/frontend tests, a frontend production build, and integration checks.

### Phase 6: Evaluation and honest analysis

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
