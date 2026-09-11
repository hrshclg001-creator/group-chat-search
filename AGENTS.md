# Search a Group Chat Properly

## Current scope

The initial task is documentation only: AGENTS.md, PLAN.md, a short README.md, and .gitignore. Do not scaffold React, FastAPI, or implement the application until a subsequent task authorizes implementation. PLAN.md describes future work, not completed functionality.

## Mandatory assessment requirements

- Build semantic search over a synthetic group chat. Never use a real or private chat.
- The corpus must contain at least 4,000 messages from exactly 8 realistic participants and span approximately 6 months.
- Include realistic Hinglish/code-mixed language, typos, one-word replies, forwarded messages, media placeholders, emojis, and messy conversational text.
- Include at least 3 long decision threads that reach concrete conclusions.
- Create 40 manually labelled evaluation queries.
- At least 8 evaluation queries must have zero meaningful word overlap with the target message. Document the overlap convention before evaluating and manually review this subset.
- Queries must include meaning/semantic searches, person-based searches, and time-based searches.
- Search must return the actual matching message plus useful surrounding conversation context. A summary or neighboring message alone does not satisfy this requirement.
- Measure Top-1 accuracy across all 40 queries and separately measure accuracy across the hard zero-word-overlap subset.
- Report the gap between these numbers honestly, in percentage points, along with both numerators and denominators.
- Do not modify expected answers merely to make evaluation results look better. Do not silently change evaluation ground truth.
- The final project must be reproducible from the README.

## Intended architecture

- Frontend: React, Vite, and plain responsive CSS.
- Backend: Python and FastAPI.
- Semantic retrieval: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` embeddings and NumPy cosine similarity.
- Lexical retrieval: TF-IDF search.
- Ranking: metadata-aware person/time ranking and hybrid ranking combining lexical, semantic, and metadata signals.
- Contextual retrieval: nearby chat messages, preserving the identity of the actual matching message.
- Data: JSONL generated deterministically using a fixed random seed, with stable participant/message IDs and timestamps.
- Evaluation: Python scripts reporting Top-1 accuracy, Recall@3, accuracy by query category, and zero-overlap accuracy. Compare the lexical baseline, semantic baseline, and hybrid approach using the same frozen corpus and query set.

## Engineering rules

- Keep components modular and responsibilities explicit.
- No external LLM API should be required for normal execution. Run embeddings locally and document the initial model download and cache requirements.
- Never commit secrets, credentials, or private chat data.
- Use deterministic test data. Record the fixed generation seed, configuration, dependency versions, and model revision for reproducibility.
- Write tests and run relevant tests after each implementation task. Record what ran and any failures or limitations; do not claim unrun checks passed.
- Do not fabricate benchmark numbers. Report only measured results with the configuration and artifacts needed to reproduce them.
- Freeze manually labelled evaluation ground truth before scoring or tuning against it. A legitimate correction requires an explicit rationale, a visible change history, and rerunning affected comparisons; never change labels solely to improve results.
- Keep evaluation labels out of retrieval inputs and ranking logic. Do not hand-code query-specific answers.
- Favor reliability and clarity over unnecessary complexity.
- Keep the README aligned with implemented behavior. By final delivery, document setup, data generation, model preparation, indexing, running both services, testing, evaluation, and limitations.

## Completion standard

Follow the phases and acceptance criteria in PLAN.md. A phase is complete only when its required behavior and relevant checks pass. Clearly identify unimplemented work and unmeasured results.
