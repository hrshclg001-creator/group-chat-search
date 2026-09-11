# Synthetic corpus review

Generator version: `1.0.0`. Seed: `20260901`. Reference runtime: Python `3.9.10`.

The generated corpus contains **4,634 messages**, exactly **eight** fictional participants, and all **184 dates** from March 1 through August 31, 2026. The reference date is September 1, 2026. All timestamps use `+05:30`.

Corpus SHA-256: `d676b0a4872d627fa3a13b8d9ab7e8b87733b3e5dccff5efd914143a9a949371`.

## Decision threads

Ranges below include intervening unrelated chat. Exact thread membership is in `corpus_metadata.json`; the conclusion is an actual message in `messages.jsonl`, not a replacement summary.

| Thread | Dates | Messages | Inclusive corpus ID range | Conclusion ID |
| --- | --- | ---: | --- | --- |
| `TRIP_MANALI` | March 8 - April 2 | 72 | `MSG_000170` - `MSG_000857` | `MSG_000713` |
| `HACKATHON_STACK` | April 10 - May 3 | 72 | `MSG_001058` - `MSG_001609` | `MSG_001482` |
| `BIRTHDAY_EVENT` | July 6 - July 25 | 72 | `MSG_003210` - `MSG_003745` | `MSG_003616` |

- Trip: Goa is initially preferred by Rohan; cost, connections, motion sickness, rest stops and cancellation conditions drive comparison with Manali. Goa and postponement are rejected. The final decision is Manali on June 10-15, Rs 8,700 maximum per person, with refundable accommodation and deposit responsibility. Charger, mess-food, assignment and lost-notebook interruptions break up the discussion. A later Goa advertisement does not reopen the decision.
- Hackathon: the first concrete proposal is MERN; Django/Postgres, Flutter, Firebase and a joking blockchain suggestion also appear. Offline judging and a small relational dataset drive rejection of cloud dependencies, a mobile app and the original starter. The final implementation note explicitly selects React/Vite/JavaScript, FastAPI/Python and SQLite with plain CSS and local images. Movie plans, badminton, food and printer chatter interrupt the technical discussion. A follow-up confirms the local setup and keeps the rejected database from returning.
- Birthday: rooftop dinner, bowling, a lawn picnic and the hostel common room are rejected for price, rain or access constraints. The final choice is the Nukkad Cafe side room on July 25, 7-9 pm, Rs 2,400 for snacks/drinks plus Rs 500 for cake; Rs 2,900 total under a Rs 3,000 ceiling, split eight ways at Rs 362.50 each. Cats, umbrellas, a homemade card and Wi-Fi interruptions act as distractors. The post-event conversation confirms the same actual fictional total.

All three threads have six dated episodes, all eight speakers, concrete responsibilities and follow-up. The earlier alternatives remain in the corpus. Thread/conclusion annotations are corpus audit information only: no evaluation queries or ranking rules have been authored.

## Content and checks

Observed message types: 4,324 text, 44 forwarded, 51 URL, 134 image, 24 PDF and 57 voice placeholders. The corpus includes English, Romanized Hindi/Hinglish, misspellings, emojis and standalone `haan`, `done`, `ok`, and `😂`. Background topics cover college, assignments, exams, coding, food, movies, travel, events and random chatter. All names, institutions, quotes, transactions and notices are fictional. Links and media are not fetched or downloaded.

Review covered all 18 authored decision episodes and generated daily episodes from the 15th of each month, plus automated checks over every record. Samples showed coherent speaker replies and shared episode details. Initial review found overly regular daily activity; generation was revised to use 2-4 episodes per day and varied casual wording. The final samples were reviewed after regeneration. This was not an exhaustive manual read of all 4,634 messages.

The generator and standalone validator passed. The backend suite passed **32 tests**, including 27 corpus tests and five existing API tests. Corpus tests cover structural and calendar requirements, decision outcomes and distractors, hash and artifact consistency, independent byte-identical runs, and malformed or tampered data. Both output files were regenerated twice in separate test directories and matched byte-for-byte. One early validation failure caught a missing literal `ok` reply; it was fixed before the successful final runs.

Limitations: 56 background vignette templates generate recurring situations; substantial repeated phrasing remains, and participant profiles are light characterization rather than simulated personal histories. Daily conversations are eight messages each even though their number and timing vary. This is suitable for a reproducible synthetic assessment corpus, not a model of the full diversity of real group chats. No search quality or benchmark accuracy has been measured.
