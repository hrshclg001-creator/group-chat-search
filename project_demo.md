# RecallChat — Project Demonstration Script

**Assessment:** Search a Group Chat Properly  
**Target duration:** Approximately 8 minutes, including search wait times  
**Format:** Screen recording with spoken narration  
**Evidence:** Current repository implementation, saved API responses and measured benchmark results

Use the quoted paragraphs as narration. The action lists and presenter notes are recording directions, not lines to read aloud. Results listed below were observed in repository artifacts; rehearse against the running application before recording. If a live result differs, describe what appears rather than reading the expected result as though it happened.

## Before recording

1. Complete installation using [README.md](README.md). The verified environment is Windows with Python 3.9.10, Node 24.8.0 and npm 11.6.0.
2. Prepare both local models before filming. From the repository root:

   ```powershell
   cd backend
   .\.venv\Scripts\python.exe -m scripts.prepare_model
   .\.venv\Scripts\python.exe -m scripts.prepare_reranker
   cd ..
   ```

3. If you want fresh benchmark and test evidence in the recording, run these sequentially **before starting the backend**. The benchmark and server both load models, so avoid running them together on a constrained machine.

   ```powershell
   # Repository root
   .\backend\.venv\Scripts\python.exe -m evaluation.validate_queries
   .\backend\.venv\Scripts\python.exe evaluation/evaluate.py --all
   .\backend\.venv\Scripts\python.exe -m evaluation.evaluate_bilingual

   cd backend
   .\.venv\Scripts\python.exe -m pytest -q
   cd ..
   .\backend\.venv\Scripts\python.exe -m pytest evaluation/tests -q

   cd frontend
   npm.cmd test
   npm.cmd run build
   cd ..
   ```

   Keep the completed terminal output available. If you use saved reports instead, identify them as saved measured results. Do not imply that an evaluation finished during the recording when it did not.

4. Start the services in two terminals, each initially at the repository root. If they are already running, use the existing instances.

   **Terminal 1 — backend:**

   ```powershell
   cd backend
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

   **Terminal 2 — frontend:**

   ```powershell
   cd frontend
   npm.cmd run dev
   ```

   This recording command omits automatic reload so incidental file edits do not restart model initialization. Wait for application startup to complete. A successful health check alone does not prove search is ready; submit a rehearsal search as well.

5. Open these views in advance:

   - Application: `http://127.0.0.1:5173`
   - Optional API documentation: `http://127.0.0.1:8000/docs`
   - IDE: `backend/data/corpus_metadata.json`, `evaluation/queries.json`, `results/evaluation_summary.md`, `results/benchmark.png`, and this script

6. Use a readable browser zoom and editor font. Close unrelated windows and mute notifications. Rehearse the copy-ready queries at the end of this document. Allow several seconds for broad searches; keep the loading state visible.

Linux/macOS equivalents are in the README. The commands above are intended for the verified Windows setup.

## Recording script

### 0:00–0:30 — Introduce the problem

**On screen:** The RecallChat home screen, including its title, subtitle and search input.

**Say:**

> “This is RecallChat, my project for the Search a Group Chat Properly assessment. It searches a group-chat archive by meaning, participant and time. The problem is that we often remember what a conversation meant without remembering the exact words. The result should identify the original message and show enough surrounding conversation to understand it.”

### 0:30–1:00 — Establish the dataset

**Actions:** Point to the corpus statistics. Briefly open `backend/data/corpus_metadata.json`, then return to the application.

**Say:**

> “The archive is entirely synthetic. It contains 4,634 messages from eight fictional Indian students, covering March through August 2026. It includes English, Hinglish, typos, one-word replies, emojis, forwards and media placeholders. Three extended discussions reach decisions about a Manali trip, a hackathon stack and a birthday event. Generation uses a fixed seed, so the corpus can be reproduced.”

**Presenter note:** Do not describe this as an imported WhatsApp chat. Media placeholders are not analyzed images, audio or PDFs.

### 1:00–1:50 — Find a decision and inspect its context

**Actions:**

1. Click the **“When did we decide on Manali?”** example chip.
2. Let the loading state finish.
3. Point to the highlighted matching bubble, sender and timestamp.
4. Click **Show more context** on the first result.
5. Point to the relevance score and displayed search latency.

**Say:**

> “I remember the destination, but I want the actual decision. The matching message is from Ishita on March 28. It confirms Manali for June 10 to 15, a maximum of 8,700 rupees each, and the deposit arrangement. The March timestamp tells us when the decision was sent; June is when the trip was planned.”

> “The highlighted bubble is the retrieved original message. The quieter bubbles are neighboring messages in chronological order. Expanding context helps interpret the discussion, including its interruptions. The relevance score is a ranking signal, not a confidence percentage.”

**Presenter check:** The captured first hit is `MSG_000713`, beginning `Final decision: Manali, June 10-15...`. IDs are available in API/report artifacts; the UI does not need to display them. Context is limited to three messages per side within 30 minutes, not the entire decision thread.

### 1:50–2:35 — Demonstrate person and relative-time filtering

**Actions:** Replace the input with this query and press **Enter**:

```text
What network maintenance notice did Meera forward last month?
```

Point to **Person: Meera Nair**, **Time: August 2026**, and the matching forwarded notice.

**Say:**

> “This combines a sender, a relative time period and a request for a forwarded item. The parser recognizes Meera and resolves last month to August 2026. The archive uses September 1, 2026 as its fixed reference date, so the answer does not depend on the day I record this video.”

> “Explicit sender, date and message-type constraints filter candidate messages before final ranking. The matching message is Meera’s forwarded network-maintenance notice for August 6. Surrounding context can contain other speakers, but the matching message must satisfy the filters.”

**Presenter check:** Q038 retrieves `MSG_003999`, beginning `Forwarded: Campus network maintenance, 2026-08-06...`. The forwarded-type constraint exists in API metadata; do not claim the UI has a separate type badge.

### 2:35–3:15 — Search in Hinglish

**Actions:** Submit:

```text
Meera ko August 21 ko kaunsi reference book mili thi?
```

Point to the returned message and the **preferred** person badge.

**Say:**

> “Now I’m asking in Hinglish: which reference book did Meera find on August 21? The matching message says she found the Software Engineering reference book in the library. The original Hinglish text is preserved.”

> “This wording mentions Meera without explicitly saying ‘message from Meera,’ so the parser treats her as a preferred participant rather than a strict author filter. The August 21 date is still a filter. That distinction is visible in the interpretation.”

**Presenter check:** The captured first hit is `MSG_004346`. Its API interpretation is `person_mode: bonus` with both date bounds equal to `2026-08-21`. Do not describe every recognized name as a hard filter.

### 3:15–3:55 — Show a genuine zero-overlap success

**Actions:** Submit:

```text
What restriction prevented the birthday gathering from using the dorm lounge?
```

**Say:**

> “This is one of the frozen zero-word-overlap questions. The target says: ‘Hostel common room can’t allow outside students after 6 that day.’ The query uses different content words, such as ‘dorm lounge’ instead of ‘hostel common room.’ Under the documented tokenization and stopword convention, the query and original target text have no meaningful word overlap.”

> “This example succeeds, but it is the only one of the ten hard questions that the current hybrid system gets right at rank one. I’ll show the full results shortly.”

**Presenter check:** Q006 targets and retrieves `MSG_003418`. Zero overlap is measured against the original target text; it does not mean context and metadata provide no clues.

### 3:55–4:35 — Demonstrate a real limitation

**Actions:** Submit:

```text
What made a seaside holiday unaffordable?
```

Inspect the highlighted message. If useful, open `results/failed_queries.txt` and find `Q001` under the hybrid section.

**Say:**

> “Here is a failure. The intended answer explicitly rejects Goa because its total exceeds the spending cap. The current first result is a nearby message accepting that the sea trip should wait and mentioning cancellation terms. It is related, but it does not explain the cost restriction.”

> “The correct explanation may appear in the surrounding context. That still counts as an incorrect Top-1 result because evaluation requires the matching message itself to be correct. I kept this failure in the benchmark instead of changing the expected answer.”

**Presenter check:** Q001 expects `MSG_000600`: `Goa rejected for this break because total exceeds our cap`. The saved first hit is `MSG_000599`: `fine yaar sea next time. don't book without cancellation clause`.

### 4:35–5:30 — Explain how the system works

**Actions:** Expand **About this search**. Then briefly show `backend/app/search/reranker_config.py` and the architecture in the README.

**Say:**

> “The frontend is React with Vite and plain CSS. FastAPI serves search and corpus statistics. A deterministic parser identifies participants and date constraints. Retrieval combines multilingual message embeddings, contextual embeddings and word-and-character TF-IDF features.”

> “Eligible candidates then go through a local multilingual cross-encoder. It reads the question together with each original message and its sender and date. It does not receive neighboring answers or evaluation labels. Its score contributes 85 percent of the final score, with 15 percent from the first-stage hybrid ranker.”

> “Both models load once per backend process. Document embeddings are cached, while each search encodes the query and reranks candidates. No external LLM API is required. Initial model preparation downloads public weights, but normal inference runs locally.”

**Presenter notes:**

- Embedding context: up to two previous and two following messages within 30 minutes.
- Candidate union: top 128 eligible messages per original-semantic, contextual-semantic, lexical and hybrid signal; at most 512 for API requests.
- The original embedding model is `paraphrase-multilingual-MiniLM-L12-v2`; the reranker is `mmarco-mMiniLMv2-L12-H384-v1`. Revisions and settings are pinned in code.
- A cross-encoder scores query–message pairs; it does not generate an answer or summary.

### 5:30–6:40 — Present the measured evaluation

**Actions:** Show `results/benchmark.png`, then `results/evaluation_summary.md`. Keep the overall and hard columns readable. Show completed benchmark output only if you actually ran it before recording.

**Say:**

> “The main benchmark uses the same 40 frozen labelled queries for all four methods. Lexical Top-1 accuracy is 22.5 percent, original semantic retrieval is 32.5 percent, contextual-only retrieval is 10 percent, and the final hybrid pipeline is 62.5 percent.”

> “Hybrid retrieves the correct first message for 25 of 40 queries and finds it within the top three for 29 of 40. But hard zero-overlap accuracy is only one out of ten, or 10 percent. The overall-versus-hard gap is 52.5 percentage points. That gap is a major limitation.”

> “Adding the reranker improved overall Top-1 from 22 to 25 correct answers. Person accuracy increased from seven to ten out of ten, while time accuracy fell from eight to seven out of ten. I retained those regressions in the report.”

> “A separately frozen bilingual supplement improved from eight to seventeen correct answers out of twenty-four, including Hinglish from three to seven out of twelve. These are paired development examples, not independent held-out evidence. The original forty queries were not replaced.”

**Reference table — use the current saved report if results have changed:**

| Method | Top-1 | Recall@3 | Hard Top-1 |
| --- | --- | --- | --- |
| Lexical | 9/40 (22.5%) | 16/40 (40%) | 0/10 (0%) |
| Semantic | 13/40 (32.5%) | 16/40 (40%) | 1/10 (10%) |
| Contextual | 4/40 (10%) | 12/40 (30%) | 1/10 (10%) |
| Hybrid | 25/40 (62.5%) | 29/40 (72.5%) | 1/10 (10%) |

### 6:40–7:15 — Show engineering and reproducibility evidence

**Actions:** Briefly show the completed test/build output or the recorded checks in `results/tuning_notes.md`. Open the README setup section.

**Say:**

> “The latest recorded verification passed 232 backend tests, 42 evaluation tests, 22 frontend tests and the production build. Tests cover constraints, original-message identity, API behavior, malformed model caches and local reranker inference. The corpus and evaluation inputs have integrity checks, and dependencies and model revisions are pinned.”

> “The README includes setup, model preparation, both services, evaluation and testing commands. Broad queries can take several seconds, and the second model adds memory and startup cost. Browser acceptance checks and a fresh installation of this two-model version remain outstanding.”

**Presenter note:** The earlier fresh Windows installation audit predates the reranker. Do not present it as a fresh clean-machine verification of the current two-model version. Update spoken test counts if your new run differs.

### 7:15–7:40 — Close

**On screen:** Return to RecallChat with the Manali decision or Hinglish result visible.

**Say:**

> “RecallChat demonstrates retrieval of original chat messages using meaning, lexical clues, metadata and conversation context. The measured improvements are useful, but difficult paraphrases and some decision questions still fail. My next steps would be independent bilingual evaluation and better conversation-specific ranking, rather than adding rules for individual benchmark questions. The implementation, results and limitations are all documented in the repository.”

## Copy-ready query order

Use these exact strings for the main recording:

```text
When did we decide on Manali?
```

```text
What network maintenance notice did Meera forward last month?
```

```text
Meera ko August 21 ko kaunsi reference book mili thi?
```

```text
What restriction prevented the birthday gathering from using the dorm lounge?
```

```text
What made a seaside holiday unaffordable?
```

## Optional 30-second API segment

If the evaluator wants backend evidence, open `/docs`, expand `POST /api/search`, choose **Try it out**, and submit:

```json
{
  "query": "When did we decide on Manali?",
  "top_k": 3
}
```

Point to `interpreted_query`, `search_time_ms`, and the first result's `matching_message`, context arrays, score fields and `rank`.

**Say:**

> “The UI calls this endpoint. The response contains the actual matching message, bounded neighboring messages, interpretation, individual score signals and measured latency. The corpus statistics come from a separate stats endpoint.”

Optionally execute `GET /api/stats` and show `message_count: 4634` and `participant_count: 8`. The recorded examples under `examples/` are real prior API responses; label them as saved examples if you show them instead of executing the endpoint.

## If something goes wrong during recording

| Situation | What to do and say |
| --- | --- |
| Search is taking several seconds | Keep the loading state visible. Explain that candidate reranking runs locally on CPU. Read the actual latency when it finishes. |
| Search returns HTTP 503 | Stop the live-search segment, inspect backend startup logs and complete both model-preparation commands. Health and stats can still work when search is unavailable. |
| A result differs from this script | Explain the visible result and verify it against the original corpus. Do not silently substitute a saved successful response. |
| The benchmark takes too long for the video | Show a clearly labelled completed run or saved measured report, and point to its reproduction command. |
| A test fails | Report the failing check. Do not read the historical passing count as a result of the failed run. |

## After recording

- Add the actual video URL to the README's Demo section.
- Check that search input, matching bubbles, interpretation badges and benchmark counts are readable in the recording.
- If you shorten the video, retain one semantic result, the person/time demonstration, the hard-query limitation and the measured overall/hard gap.
- Keep this script aligned with the current saved results; it is a presentation guide, not a replacement for running the project.
