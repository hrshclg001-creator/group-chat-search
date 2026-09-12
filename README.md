# RecallChat

**Search a Group Chat Properly**

RecallChat is a semantic and metadata-aware search engine for group-chat history. It retrieves original messages matching user intent even when exact keywords differ, and returns results with surrounding conversation context for interpretation. Hybrid retrieval combines multilingual semantic embeddings, lexical matching, and participant/temporal metadata, ranked by relevance and evaluated on 40 frozen queries including 10 zero-word-overlap paraphrases.

## Problem

Keyword search fails when users and messages use different words for the same concept. A user searching for _"unforeseen expenses"_ cannot find a message that says _"emergency buffer"_. This problem worsens with:

- **Paraphrased intent:** Meaning-based matches require semantic understanding, not just keyword overlap.
- **Code-mixed language:** Indian English mixed with Romanized Hindi (Hinglish) like _"overnight buses do back to back honge?"_ requires multilingual embeddings.
- **Short replies:** Messages like _"haan pakka"_ (okay, confirmed) are meaningless in isolation but clear in context.
- **Multiple decision stages:** A trip discussion might span questions (_"where should we go?"_), proposals (_"let's try Manali"_), and decisions (_"Manali confirmed, June 10-15"_). Keyword overlap doesn't distinguish the answer from earlier debate.
- **Temporal references:** _"last week"_ means different dates depending on when you search. A fixed reference date is needed for reproducibility.

**Example:** A user asks _"When did we decide where to travel?"_ Lexical search might miss the final decision message: _"theek hai bhai fir Manali pakka"_ (okay, so Manali it is then).

RecallChat solves this by combining semantic retrieval, metadata constraints, and contextual understanding.

## Solution

RecallChat retrieves the _original message_ that answers the user's question, preserving the actual sender, timestamp, and surrounding conversation context. It combines three search strategies:

1. **Semantic embeddings:** Local multilingual embeddings (sentence-transformers) match meaning, not keywords.
2. **Lexical matching:** TF-IDF with character n-grams tolerates typos (_nhi_ vs _nahi_).
3. **Metadata filtering:** Participant names and temporal expressions are parsed deterministically and applied as constraints.

A hybrid ranker combines these signals and returns results ranked by relevance, with up to three adjacent messages per side to make short replies interpretable.

## Features

- **Semantic retrieval** using local multilingual embeddings (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)
- **Lexical retrieval** with TF-IDF and character n-gram features (tolerates typos and spelling variation)
- **Contextual embeddings** that incorporate up to two previous and two following messages (within 30 minutes) to interpret short or ambiguous replies
- **Participant-aware search** with deterministic name parsing for explicit sender queries (English and Hinglish)
- **Temporal search** using a fixed reference date to resolve relative expressions (_"last month"_, _"yesterday"_) reproducibly
- **Hybrid ranking** that combines semantic, lexical, and metadata signals with visible weights and constraints
- **Surrounding conversation context** preserved for interpretation; original message ID always returned
- **Measured evaluation** on 40 frozen queries including 10 zero-word-overlap paraphrases
- **No external LLM API** required; all inference runs locally on CPU

## Architecture

```
User Query (React UI)
    |
    v
Query Parser
    +---- Participant detection (Hinglish & English)
    +---- Temporal expression parsing
    +---- Message-type detection (forwarded, attachment, etc.)
    |
    v
Semantic Retrieval          Lexical Retrieval
    |                              |
    +---- Original embeddings      +---- TF-IDF word/char n-grams
    +---- Contextual embeddings    |
    |                              |
    +----- (All messages scored)---+
                 |
                 v
         Hybrid Ranker
                 |
    +---- Combine semantic, lexical, person, time
    +---- Apply metadata constraints
    +---- Deterministic tie-breaking
    |
    v
  Ranked Results
    |
    v
Contextual Assembly
    +---- Original message
    +---- Up to 3 neighbors per side (within 30 min)
    +---- Chronological order
    |
    v
React UI Display
    +---- Highlighted matching message
    +---- Metadata badges (sender, time, relevance score)
    +---- Expandable context
    +---- Search latency and corpus statistics
```

## Tech Stack

| Component             | Technology                           | Version                           |
| --------------------- | ------------------------------------ | --------------------------------- |
| **Backend**           | Python/FastAPI                       | 3.115.12 / 3.9+                   |
| **Web server**        | Uvicorn                              | 0.34.3                            |
| **Embeddings**        | sentence-transformers                | 3.4.1                             |
| **Semantic model**    | Hugging Face Transformers            | 4.48.3                            |
| **Tensor backend**    | PyTorch                              | 2.6.0                             |
| **Numerical compute** | NumPy/SciPy                          | 2.0.2 / 1.13.1                    |
| **Lexical retrieval** | scikit-learn                         | 1.6.1                             |
| **Frontend**          | React + Vite                         | Latest (package-lock.json pinned) |
| **Styling**           | Plain CSS (responsive, no framework) | —                                 |
| **Evaluation**        | Matplotlib                           | 3.9.4                             |
| **Testing**           | pytest / vitest                      | 8.4.2                             |

## Dataset

**All data is entirely synthetic.** No real or private group chat was used.

| Property                 | Value                                                                                                                         |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| **Messages**             | 4,634 JSONL records                                                                                                           |
| **Participants**         | 8 fictional students: Aarav Sharma, Aditya Joshi, Ananya Verma, Ishita Patel, Kabir Khan, Meera Nair, Rohan Mehta, Sneha Iyer |
| **Date range**           | 2026-03-01 through 2026-08-31 (all 184 calendar dates)                                                                        |
| **Timezone**             | Asia/Kolkata (UTC+05:30)                                                                                                      |
| **Fixed reference date** | 2026-09-01 (for reproducible temporal parsing)                                                                                |
| **Generation seed**      | 20260901 (deterministic)                                                                                                      |
| **Seed version**         | 1.0.0                                                                                                                         |
| **Corpus SHA-256**       | `d676b0a4872d627fa3a13b8d9ab7e8b87733b3e5dccff5efd914143a9a949371`                                                            |

### Message Characteristics

- **English + Hinglish:** Messages mix English with Romanized Hindi; examples: _"overnight buses do back to back honge?"_, _"haan pakka"_, _"that reel starts from Mumbai, hum Indore mein hain"_
- **Typos & misspellings:** _"nhi"_, _"thnks"_, _"dont"_ (intentionally generated)
- **Short replies:** 396 single-token messages including _"haan"_, _"done"_, _"ok"_, emoji-only replies
- **Forwarded text:** 44 messages marked as forwards, preserving original wording
- **Media placeholders:** 134 images, 24 PDFs, 57 voice messages marked as `[Image]`, `[PDF]`, `[Voice message]`
- **URLs:** 51 fictional example-domain links
- **Emojis:** Natural conversational emoji use (😅, 😭, etc.)
- **Topics:** College life, assignments, exams, travel, food, movies, coding, casual chatter

### Decision Threads

Three structured **72-message decision threads** (each spanning six dated episodes):

| Thread            | Topic                                   | Alternatives                                           | Final Decision                                          | Conclusion Message |
| ----------------- | --------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------- | ------------------ |
| `TRIP_MANALI`     | Where to travel, summer vacation        | Goa vs. Manali; cost negotiations                      | Manali, June 10–15, ₹8,700 per person cap               | MSG_000713         |
| `HACKATHON_STACK` | Technology stack for hackathon          | MERN, Django/Postgres, Flutter/Firebase, React/FastAPI | React + Vite + JavaScript; FastAPI + Python + SQLite    | MSG_001482         |
| `BIRTHDAY_EVENT`  | Venue and cost for birthday celebration | Rooftop dinner, bowling, lawn picnic, common room      | Nukkad Cafe side room, July 25, ₹2,900 under ₹3,000 cap | MSG_003616         |

Each thread includes rejected alternatives, interruptions, calculations, and follow-up messages.

## Search Pipeline

### 1. Query Parsing

The deterministic parser extracts metadata from natural-language queries without calling an external LLM:

- **Participant detection:** Matches full names, first+last, or unambiguous first names against corpus metadata. English requests (_"what did Ishita say"_) and Hinglish (_"Ishita ne"_) are both recognized. Uncertain matches receive a small relevance bonus; names mentioned as topics do not become filters.
- **Temporal expression resolution:** Recognizes _today_, _yesterday_, _last week_, _last month_, _this month_, explicit month names, ISO dates, named dates, and simple ranges. **Uses the fixed reference date (2026-09-01), never the system clock.** Supported Hinglish forms include _"pichle month"_ (last month).
- **Message-type detection:** Explicit requests for forwarded items, PDFs, images, voice messages or URLs filter by stored message type.

Example: _"What did Ishita send last month?"_ → participant: Ishita Patel, date range: August 2026, no type constraint.

### 2. Semantic Retrieval

Local inference using `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (pinned revision `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`):

- Encodes all 4,634 messages and incoming queries to 384-dimensional normalized vectors
- Computes NumPy cosine similarity to rank candidates
- Handles Hinglish and English transparently; no translation required
- Supports two representations:
  - **Original-only:** The message text as-is
  - **Contextual:** Message text plus up to 2 previous and 2 following messages (within 30 minutes), with role markers

Contextual embeddings help interpret short replies but risk adding unrelated chatter.

### 3. Lexical Retrieval

TF-IDF with dual features:

- **Word features:** Unigrams and bigrams with cosine similarity
- **Character features:** 3–5 character n-grams (`char_wb` mode) for typo tolerance
- **Combined score:** 0.70 × word cosine + 0.30 × character cosine

No embeddings required; runs locally in milliseconds.

### 4. Metadata Filtering & Constraints

Parsed constraints intersect:

- **Author filter:** Explicit sender requests narrow candidates to messages from that participant
- **Date filter:** Temporal expressions constrain the message timestamp
- **Type filter:** Explicit attachment/forwarded-item requests filter by message type
- **Empty result handling:** If the intersection is empty, no results are returned; constraints are not silently relaxed

### 5. Hybrid Ranking

Combines normalized scores with learned weights (visible in [ranking_config.py](backend/app/search/ranking_config.py)):

| Signal                       | No constraint | With hard constraint |
| ---------------------------- | ------------- | -------------------- |
| Contextual semantic          | 0.35          | 0.25                 |
| Original semantic            | 0.35          | 0.45                 |
| Lexical                      | 0.20          | 0.20                 |
| Person bonus (if applicable) | 0.05          | 0.05                 |
| Date bonus (if applicable)   | 0.05          | 0.05                 |

When an author or date constraint applies, 0.10 weight shifts from contextual to original-message similarity (to prioritize direct message text).

Exact ties broken by ascending message ID (deterministic).

### 6. Contextual Assembly

For each ranked result:

- Return the original matching message (ID, text, sender, timestamp, scores)
- Append up to 3 chronologically-adjacent messages before it (within 30 minutes)
- Append up to 3 chronologically-adjacent messages after it (within 30 minutes)
- Never include a neighbor as a correct hit during evaluation

### 7. API Response

FastAPI returns:

```json
{
  "query": "...",
  "query_metadata": { "detected_participant": "...", "detected_date_range": "...", ... },
  "search_time_ms": 45,
  "results": [
    {
      "rank": 1,
      "matching_message": { "id": "MSG_XXX", "text": "...", "sender": "...", "timestamp": "..." },
      "scores": { "hybrid": 0.85, "semantic": 0.90, "lexical": 0.75, "person_bonus": 0.05, ... },
      "previous_messages": [ { "id": "...", "text": "...", ... }, ... ],
      "next_messages": [ ... ]
    }
  ]
}
```

## Why Context Matters

Short replies are unintelligible in isolation. A message _"haan pakka"_ (okay, confirmed) provides no semantic signal about the topic—is it about travel, food, homework, or an event?

**Without context:**

```
Query: "When did we confirm the trip?"
Result: MSG_001200 "haan pakka"
→ Useless; sender and topic unknown.
```

**With context:**

```
Query: "When did we confirm the trip?"
Result: MSG_001200 "haan pakka"
  Previous: Rohan: "So June 10-15, Rs 8700 cap. Everyone okay?"
  Previous: Aditya: "Yes, Manali final."
→ Clear: Trip confirmed June 10-15 to Manali.
```

Contextual embeddings encode the surrounding messages, allowing the embedding space to distinguish _"haan pakka"_ in a travel context from the same phrase in a food discussion. However, context also risks pulling in unrelated chatter—a risk our evaluation captures.

## Evaluation

**Measured on 40 frozen queries against 4,634 synthetic messages.** Reference date: 2026-09-01.

### Benchmark Results

| Method         |  Top-1 Accuracy   |     Recall@3      |  Hard-10 Top-1   |      Person      |       Time       |     Semantic     | Gap (pp)  |
| -------------- | :---------------: | :---------------: | :--------------: | :--------------: | :--------------: | :--------------: | :-------: |
| **Lexical**    |   22.5% (9/40)    |   40.0% (16/40)   |   0.0% (0/10)    |   30.0% (3/10)   |   30.0% (3/10)   |   15.0% (3/20)   |   +22.5   |
| **Semantic**   |   32.5% (13/40)   |   40.0% (16/40)   |   10.0% (1/10)   |   30.0% (3/10)   |   40.0% (4/10)   |   30.0% (6/20)   |   +22.5   |
| **Contextual** |   10.0% (4/40)    |   30.0% (12/40)   |   10.0% (1/10)   |   10.0% (1/10)   |   20.0% (2/10)   |   5.0% (1/20)    |    0.0    |
| **Hybrid**     | **55.0% (22/40)** | **62.5% (25/40)** | **10.0% (1/10)** | **70.0% (7/10)** | **80.0% (8/10)** | **35.0% (7/20)** | **+45.0** |

- **Top-1:** Correct message ID ranked first
- **Recall@3:** Correct message appears in top 3 results
- **Hard-10:** Zero-word-overlap subset (Q001–Q010)
- **Category breakdown:** Person-based, time-based, and semantic queries (by primary label)
- **Gap:** Overall Top-1 minus Hard-10 Top-1 (percentage points)

Hybrid achieves **55% overall accuracy** but only **10% on hard paraphrases**, indicating that person/time metadata help more than semantic paraphrase understanding.

Contextual embeddings alone perform _worse_ than original-only embeddings (10% vs 32.5%), showing that adding adjacent messages is not automatically beneficial.

All three baselines (lexical, semantic, contextual) remain **unchanged** and are **always compared** using the same frozen inputs. No labels or ranking settings were modified during evaluation.

### Benchmark Artifacts

Run `python evaluation/evaluate.py --all` to regenerate:

- `results/comparison.csv` — Numeric results
- `results/comparison.json` — Detailed metrics and per-query results
- `results/benchmark.png` — Overall and hard-subset accuracy chart
- `results/failed_queries.txt` — Expected vs. retrieved messages for all failures
- `results/evaluation_summary.md` — Auto-generated summary

## Hard Query Evaluation

**Zero-word-overlap queries (Q001–Q010)** test whether the search engine understands meaning when exact keywords are absent.

### Overlap Convention

Before labelling, a versioned tokenization and stopword list was fixed in [evaluation/OVERLAP.md](evaluation/OVERLAP.md):

1. **Text-only comparison:** Query text vs. message text; sender, timestamp, and metadata excluded.
2. **Unicode NFKC normalization and casefolding** (case-insensitive)
3. **Contraction expansion:** _"can't"_ → _"can not"_, _"won't"_ → _"will not"_
4. **Tokenization:** Letters and digits only; punctuation, emojis, URLs are separators
5. **Fixed stopword list:** Only explicit function words (English + Romanized Hindi) are removed; negation, quantities, time references, and content words are kept
6. **No stemming, translation, or spelling correction**

A query has zero-word-overlap when both content-token sets are nonempty and their intersection is empty.

### Examples

**Q001:** _"What made a seaside holiday unaffordable?"_ → Expected: MSG_000600

Corpus message:

```
Ishita Patel: "Goa's total is over 8700 budget. Nope not doable."
```

Content tokens (after normalization):

- Query: `{seaside, holiday, unaffordable}`
- Message: `{goa, total, 8700, budget, nope, not, doable}`
- Intersection: ∅ (empty)

Despite zero lexical overlap, semantic retrieval should recognize _"seaside holiday"_ → _"Goa"_ and _"unaffordable"_ → _"over budget"_.

**Q009:** _"How much of our holiday allowance was reserved for unforeseen expenses rather than souvenirs?"_ → Expected: MSG_000700

Corpus message:

```
Ishita Patel: "We should keep 700 emergency buffer out of 8700 and not spend it on shopping."
```

Semantic test: _"unforeseen expenses"_ ≈ _"emergency buffer"_, _"souvenirs"_ ≈ _"shopping"_.

### Semantic Relationship Review

All 10 hard queries underwent manual review to confirm they are substantive paraphrases, not mere spelling tricks. See [evaluation/HARD_SUBSET_REVIEW.md](evaluation/HARD_SUBSET_REVIEW.md) for complete details.

Current performance: Hybrid retrieves only 1 of 10 hard queries correctly (10%), leaving 9 failures primarily in semantic understanding and paraphrase recognition.

## Running Locally

### Prerequisites

- **Python 3.9+** with `venv` support
- **Node.js 20.19+** with npm
- **Internet access** (initial setup only, for model download)
- **~1 GB** disk space for dependencies, model weights (~450 MiB) and embeddings

Tested on Windows (Python 3.9.10, Node 24.8.0, npm 11.6.0). Linux commands provided but not clean-install verified.

### Windows Setup (PowerShell)

```powershell
# Create and activate Python virtual environment
py -3.9 -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock.txt
.\backend\.venv\Scripts\python.exe -m pip check

# Install frontend dependencies
cd frontend
npm.cmd ci
cd ..
```

### Linux/macOS Setup (Bash)

```bash
# Create and activate Python virtual environment
python3.9 -m venv backend/.venv
./backend/.venv/bin/python -m pip install -r backend/requirements.lock.txt
./backend/.venv/bin/python -m pip check

# Install frontend dependencies
cd frontend
npm ci
cd ..
```

**Note:** `requirements.lock.txt` pins the exact tested package set (58 packages, Windows). Platform-specific transitive dependencies may differ on Linux/macOS; `requirements.txt` lists direct dependencies only.

### Generate Corpus

The corpus is pre-generated at `backend/data/messages.jsonl`. Regeneration is optional and deterministic.

**Windows:**

```powershell
cd backend
.\.\venv\Scripts\python.exe -m scripts.generate_data
.\.\venv\Scripts\python.exe -m scripts.validate_data
cd ..
```

**Linux/macOS:**

```bash
cd backend
./.\venv/bin/python -m scripts.generate_data
./.\venv/bin/python -m scripts.validate_data
cd ..
```

Generation uses only the Python standard library. To output to a custom directory, use `--output-dir PATH`.

### Prepare Embeddings & Indexes

Download the pinned sentence-transformers model and build both original and contextual embedding caches:

**Windows:**

```powershell
cd backend
.\.\venv\Scripts\python.exe -m scripts.prepare_model
.\.\venv\Scripts\python.exe -c "from app.search.corpus import load_corpus; from app.search.hybrid import HybridSearch; engine = HybridSearch(load_corpus()); print('Indexed', len(engine.messages), 'messages')"
cd ..
```

**Linux/macOS:**

```bash
cd backend
./.\venv/bin/python -m scripts.prepare_model
./.\venv/bin/python -c "from app.search.corpus import load_corpus; from app.search.hybrid import HybridSearch; engine = HybridSearch(load_corpus()); print('Indexed', len(engine.messages), 'messages')"
cd ..
```

Model files are cached in `.cache/models/` (ignored by `.gitignore`). Embeddings are cached in `.cache/embeddings/` keyed by corpus hash, model revision, and settings. Missing caches are rebuilt automatically at server startup or evaluation, so explicit indexing is optional.

### Start Backend

**Windows:**

```powershell
cd backend
.\.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Linux/macOS:**

```bash
cd backend
./.\venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend starts on `http://127.0.0.1:8000`. API documentation: `http://127.0.0.1:8000/docs`.

**Health check:** `http://127.0.0.1:8000/api/health` returns `{"status":"ok"}` when the service is ready.

**Important:** Allow model/index initialization to finish. If initialization fails, health and stats may remain accessible while search returns HTTP 503 with setup instructions. Resolve the error and restart; health alone does not prove search is ready.

### Start Frontend

In a **second terminal**, from the repository root:

**Windows:**

```powershell
cd frontend
npm.cmd run dev
```

**Linux/macOS:**

```bash
cd frontend
npm run dev
```

Frontend starts on `http://127.0.0.1:5173`. Vite proxies `/api` requests to `http://127.0.0.1:8000` (backend).

**Open browser:** `http://127.0.0.1:5173`

### Build Frontend for Production

```powershell
# Windows
cd frontend
npm.cmd run build
cd ..
```

```bash
# Linux/macOS
cd frontend
npm run build
cd ..
```

Output is in `frontend/dist/`. This is not a complete production deployment; authentication, reverse-proxy routing, and hosting are not configured.

## Running Evaluation

Evaluate all four retrieval methods against the frozen 40-query set:

**Windows:**

```powershell
.\backend\.venv\Scripts\python.exe evaluation/evaluate.py --all
```

**Linux/macOS:**

```bash
./backend/.venv/bin/python evaluation/evaluate.py --all
```

This runs lexical, semantic, contextual, and hybrid retrieval against identical frozen inputs (corpus, queries, overlap convention). No running API or frontend is required.

**Alternatives:**

- Single method: `python evaluation/evaluate.py --method hybrid` (or lexical, semantic, contextual)
- Compare saved reports (no rerun): `python -m evaluation.compare --all`

**Outputs:**

| Artifact                        | Purpose                                                                 |
| ------------------------------- | ----------------------------------------------------------------------- |
| `results/comparison.csv`        | Numeric results (Top-1, Recall@3, hard-subset, category breakdown, gap) |
| `results/comparison.json`       | Detailed metrics and per-query rankings                                 |
| `results/benchmark.png`         | Chart comparing overall vs. hard-subset accuracy                        |
| `results/lexical.json`          | Lexical method results, config, environment                             |
| `results/semantic.json`         | Original-only semantic results                                          |
| `results/contextual.json`       | Contextual semantic results                                             |
| `results/hybrid.json`           | Hybrid results (currently selected method)                              |
| `results/failed_queries.txt`    | All Top-1 failures with expected/retrieved messages and scores          |
| `results/evaluation_summary.md` | Auto-generated summary with measured hard-subset size                   |

See [results/evaluation_summary.md](results/evaluation_summary.md) for the most recent benchmark.

## Tests

**Backend tests:**

**Windows:**

```powershell
cd backend
.\.\venv\Scripts\python.exe -m pytest -q
cd ..
```

**Linux/macOS:**

```bash
cd backend
./.\venv/bin/python -m pytest -q
cd ..
```

**Evaluation tests:**

**Windows:**

```powershell
.\backend\.venv\Scripts\python.exe -m pytest evaluation/tests -q
```

**Linux/macOS:**

```bash
./backend/.venv/bin/python -m pytest evaluation/tests -q
```

**Frontend tests:**

**Windows:**

```powershell
cd frontend
npm.cmd test
npm.cmd run build
cd ..
```

**Linux/macOS:**

```bash
cd frontend
npm test
npm run build
cd ..
```

**Total tests passing:** 206 backend + 40 evaluation + 22 frontend = **268 tests** (verified in [FINAL_AUDIT.md](FINAL_AUDIT.md)).

Real-model tests (using the local sentence-transformers model) are run as part of the backend suite. Without the model prepared, they are skipped (not auto-downloaded).

## Repository Structure

```
group-chat-search/
├── frontend/
│   ├── src/
│   │   ├── components/          # Search results, interpretation, corpus stats
│   │   │   ├── AboutSearch.jsx
│   │   │   ├── CorpusStats.jsx
│   │   │   ├── Interpretation.jsx
│   │   │   ├── ResultCard.jsx
│   │   │   └── Icon.jsx
│   │   ├── api/                 # Relative API requests (/api/search, /api/stats)
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css           # Responsive design, plain CSS
│   ├── tests/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── index.html
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py        # GET /api/health
│   │   │   └── search.py        # POST /api/search, GET /api/stats
│   │   ├── query_understanding/ # Participant and date parser
│   │   │   ├── dates.py         # Temporal expression resolution
│   │   │   └── parser.py        # Full query parsing
│   │   ├── search/              # Core retrieval pipeline
│   │   │   ├── constraints.py   # Metadata filtering
│   │   │   ├── context.py       # Contextual message assembly
│   │   │   ├── corpus.py        # Message loading and validation
│   │   │   ├── embedding.py     # Embedding inference and caching
│   │   │   ├── hybrid.py        # Hybrid ranker
│   │   │   ├── lexical.py       # TF-IDF retrieval
│   │   │   ├── semantic.py      # Multilingual embedding retrieval
│   │   │   ├── message_types.py # Message type utilities
│   │   │   ├── model_config.py  # Model pinning and inference settings
│   │   │   ├── ranking_config.py # Visible weights and routing
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── conversation.py  # Display context assembly
│   │   │   └── search.py        # Search service initialization
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── config.py            # CORS, paths, settings
│   │   └── main.py              # FastAPI entry point
│   ├── scripts/
│   │   ├── generate_data.py     # Synthetic corpus generation
│   │   ├── validate_data.py     # Corpus validation
│   │   ├── prepare_model.py     # Model download and setup
│   │   ├── chat_style.py        # Message generation templates
│   │   ├── conversation_content.py
│   │   ├── corpus_config.py
│   │   ├── decision_threads.py  # Decision thread generation
│   │   └── __init__.py
│   ├── tests/
│   │   ├── test_health.py
│   │   ├── test_search_api.py
│   │   ├── test_lexical.py
│   │   ├── test_semantic.py
│   │   ├── test_hybrid.py
│   │   ├── test_contextual.py
│   │   ├── test_query_parser.py
│   │   ├── test_corpus.py
│   │   ├── test_message_types.py
│   │   └── test_model_integration.py
│   ├── data/
│   │   ├── messages.jsonl       # Synthetic corpus (4,634 messages)
│   │   ├── corpus_metadata.json # Participants, date range, counts
│   │   └── CORPUS_REVIEW.md     # Generation scope and limitations
│   ├── requirements.txt         # Direct dependencies
│   ├── requirements.lock.txt    # Full pinned environment (58 packages)
│   └── pytest.ini
├── evaluation/
│   ├── queries.json             # 40 frozen queries with labels and rationales
│   ├── freeze_manifest.json     # Corpus/query/convention hashes (before scoring)
│   ├── overlap_convention.json  # Stopword list and tokenization rules
│   ├── OVERLAP.md               # Overlap convention documentation
│   ├── HARD_SUBSET_REVIEW.md    # Manual review of 10 zero-word-overlap queries
│   ├── label_changes.md         # Change history (if any corrections made)
│   ├── evaluate.py              # Evaluation harness
│   ├── validate_queries.py      # Query validation
│   ├── compare.py               # Multi-method comparison and reporting
│   ├── metrics.py               # Metric calculations
│   ├── overlap.py               # Zero-word-overlap checking
│   ├── reporting.py             # Chart and report generation
│   ├── tune_hybrid.py           # Weight tuning utilities (historical)
│   └── tests/
│       ├── test_evaluate.py
│       ├── test_metrics.py
│       ├── test_overlap.py
│       └── test_compare.py
├── results/
│   ├── comparison.csv           # Current benchmark (numeric)
│   ├── comparison.json          # Current benchmark (detailed)
│   ├── benchmark.png            # Chart (Top-1 and hard accuracy)
│   ├── evaluation_summary.md    # Auto-generated summary
│   ├── lexical.json             # Lexical method results
│   ├── semantic.json            # Semantic method results
│   ├── contextual.json          # Contextual method results
│   ├── hybrid.json              # Hybrid method results
│   ├── failed_queries.txt       # All failures with evidence
│   ├── failure_analysis.md      # Analysis of all 18 hybrid failures
│   ├── tuning_notes.md          # Tuning decisions and trade-offs
│   ├── audit_evidence.json      # Fresh-install audit evidence (FINAL_AUDIT.md)
│   ├── hybrid_tuning.json       # Historical weight tuning trials
│   └── tuning/                  # Archived tuning experiments
│       ├── before/              # Pre-tuning results
│       ├── metadata_separation/ # Rejected experiment
│       └── revert_output.txt    # Experiment revert log
├── examples/
│   ├── search_response.json     # Example API response
│   ├── search_filtered_response.json
│   └── stats_response.json
├── .cache/                      # Ignored: model weights, embeddings, indexes
├── .gitignore
├── .gitattributes
├── AGENTS.md                    # Assessment requirements
├── PLAN.md                      # Implementation phases and status
├── FINAL_AUDIT.md               # Clean-install verification audit
├── README.md                    # This file
└── package.json                 # Root package.json (if present)
```

## Design Decisions

### Local Embeddings

We use `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` because:

- **No external LLM API** required; inference runs on CPU
- **Multilingual support** handles Hinglish transparently
- **Reproducibility:** pinned model revision ensures bit-identical embeddings across runs
- **Speed:** 384-dimensional vectors enable fast NumPy cosine similarity search

### NumPy Cosine Search

NumPy suffices for a 4,634-message corpus:

- In-memory TF-IDF and embedding arrays fit in seconds of RAM
- Cosine similarity is O(d) per query (d = embedding dimension)
- Deterministic tie-breaking via ascending message ID ensures reproducibility
- No vector database (Pinecone, Weaviate, etc.) complexity

At million-message scale, approximate nearest-neighbor search (HNSW, IVF) or a vector database becomes attractive.

### Hybrid Ranking

Semantic embeddings alone miss 22 of 40 answers. Hybrid ranking improves performance by:

- **Combining complementary signals:** Semantic scores capture meaning; lexical scores catch exact/near-exact matches; metadata constraints eliminate wrong speakers/dates
- **Visible weights:** `ranking_config.py` documents all decisions; no opaque learned ranker
- **Metadata-aware routing:** When a hard constraint applies, weight shifts toward original-message similarity to prioritize direct text

### Deterministic Data & Reference Dates

- **Fixed seed (20260901):** Corpus regenerates identically byte-for-byte; enables reproducible research
- **Fixed reference date (2026-09-01):** Temporal parsing never uses system clock; _"last week"_ always means Aug 25–31, regardless of when you search
- **Frozen corpus/queries/labels:** Evaluation captures development-set performance; enables honest reporting of trade-offs

### Synthetic Corpus

Synthetic data avoids privacy/licensing issues and enables evaluation reproducibility. Trade-off: template-based generation limits diversity and realism compared to archived real chat.

## Limitations

- **18 hybrid failures remain:** Hybrid misses 18 of 40 targets and 9 of 10 hard (zero-word-overlap) queries. Semantic paraphrase understanding and reliable current-message anchoring remain difficult.
- **Contextual embeddings underperform:** Adding adjacent messages (contextual baseline) actually _hurts_ performance vs. original-only embeddings (10% vs 32.5%), showing that unrelated neighbors outweigh interpretation benefits.
- **Development-set results:** The 40 queries informed hybrid weight selection; reported metrics are development-set accuracy, not held-out generalization estimates.
- **Limited Hinglish evaluation:** Code-mixed paraphrases like _"nausea/motion sickness"_ are tested, but reliable multilingual semantic understanding is not established.
- **Template-based corpus:** Simplified message templates and patterns limit diversity; no claim is made about real-chat quality or scale.
- **Repeated targets:** 37 distinct targets across 40 queries; the three decision conclusions appear multiple times to cover different question types.
- **Parser limitations:** Metadata grammar is bounded; unknown names, ambiguous ownership, unsupported dates and some event/chat-date distinctions remain difficult. Empty metadata intersections silently return no results.
- **No media analysis:** Attachment OCR, audio transcription and URL fetching are not implemented. `[Image]`, `[PDF]`, `[Voice message]` are placeholders.
- **Windows verification only:** Clean-install audit verified only Python 3.9.10 on Windows. Linux and newer Python versions are untested; floating-point differences may occur.
- **Browser verification incomplete:** Visual mobile/desktop layouts and interactive features (click, Enter, chip submission) could not be verified; render tests and source inspection provide partial evidence.

## Future Improvements

These are ideas for future work, not implemented features:

- **Answer-aware reranker:** Distinguish questions, proposals, decisions, and post-event updates with a learned ranker trained on independently labelled data.
- **Topic-consistent context:** Select contextual neighbors based on coherence rather than just time windows; avoids unrelated interruptions.
- **Stronger current-message emphasis:** Weight the central message more heavily within contextual embeddings.
- **Better multilingual models:** Evaluate stronger mixed-language embeddings on diverse English/Hinglish paraphrases, negation and numerical questions.
- **Extended metadata grammar:** Support ambiguity markers, negation, relative references and broader date/time forms with explicit test fixtures.
- **Held-out evaluation:** Obtain independently labelled development and test sets, grouping related threads to reduce label leakage.
- **Browser verification:** Complete platform-specific viewport and interaction testing on Windows/Linux/macOS before deployment.
- **Large-scale indexing:** Evaluate performance at million-message scale; compare vector databases and approximate nearest-neighbor algorithms.
- **Live chat ingestion:** Extend corpus loading to support new messages, incremental indexing and session management.

## Demo

Demo video: [Add video link before submission]

## Privacy

**All data is entirely synthetic.** No real or private group chat was used or imported. Participants, messages, prices, venues and transactions are fictional. Media placeholders (`[Image]`, `[PDF]`, `[Voice message]`) and URLs are example-domain only. Generation uses a fixed seed and authored conversation templates; there is no private-data connector or dependency.

For assessment purposes, the corpus is fully reproducible from the repository. See [backend/data/CORPUS_REVIEW.md](backend/data/CORPUS_REVIEW.md) and [FINAL_AUDIT.md](FINAL_AUDIT.md) for verification.

```

```
