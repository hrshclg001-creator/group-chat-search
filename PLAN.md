# Implementation plan

Status: scaffolding, corpus generation, frozen evaluation labels, and the first lexical retrieval baseline are implemented. The corpus contains 4,634 messages and the evaluation set has 40 queries, including 10 hard cases. The measured lexical run achieved Top-1 9/40, Recall@3 16/40 and hard Top-1 0/10; results are in `results/lexical.json`. Phase 1 remains partial; search API contracts and model preparation are future work. Semantic/hybrid retrieval, metadata ranking, context assembly and search UI/API are not implemented. Later work requires subsequent authorization.

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

Scaffolding, corpus and evaluation-query validation, seed/timestamp conventions, and deterministic generation checks are implemented. Health and CORS tests and frontend checks accompany the scaffold; see README.md for commands and validation. Search API schemas and model configuration remain unimplemented, so the full phase remains incomplete.

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

Partially implemented: `backend/app/search/` loads original messages and combines word unigram/bigram TF-IDF with character 3-5-gram TF-IDF. Fixed 0.7/0.3 cosine weights, positive-score filtering and stable message-ID ties were selected before scoring. Returned hits contain actual ID, sender, timestamp, original text and lexical score. Relevant retrieval tests passed. Embeddings, metadata-aware/hybrid ranking, persistent index caching and surrounding-context assembly remain unimplemented; this full phase is not complete.

Implement TF-IDF and multilingual embedding baselines independently. Add NumPy cosine similarity, person/time handling, hybrid ranking, and bounded nearby-message context. Cache embeddings/indexes with invalidation checks and stable ranking tie-breaks. Document ranking weights and tuning provenance without feeding evaluation labels into retrieval or hand-coding answers.

Acceptance: each mode returns actual corpus messages with correct IDs and useful chronological context. Tests cover scoring, stable ties, empty queries, person/time handling, context boundaries, and stale cache detection using deterministic fixtures. Confirm local embedding inference after model preparation. Run relevant retrieval tests.

### Phase 5: Search API and frontend

Expose validated search requests through FastAPI and integrate the React interface. Clearly display matching message, author, timestamp, and surrounding conversation. Support responsive layouts and loading, no-result, and error states.

Acceptance: end-to-end searches return the same hit IDs as direct retrieval, context remains associated with its hit, invalid requests produce clear errors, and the interface works on narrow and wide screens. Run API/frontend tests, a frontend production build, and integration checks.

### Phase 6: Evaluation and honest analysis

Lexical comparison leg only is measured: `python evaluation/evaluate.py --method lexical` validates frozen inputs and saves metrics, all query rankings/scores, configuration, environment and hashes to `results/lexical.json`. Top-1 is 9/40 (22.5%); Recall@3 is 16/40 (40%); hard Top-1 is 0/10 (0%); signed overall-minus-hard gap is +22.5 percentage points. Category Top-1 is semantic 3/20, person 3/10 and time 3/10. All 31 Top-1 errors were printed. No ground truth was changed and no post-result tuning was performed. 51 backend tests and 25 evaluation tests passed. Semantic and hybrid comparisons remain unmeasured, so Phase 6 is incomplete.

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
