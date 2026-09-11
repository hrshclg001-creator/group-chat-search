# Evaluation label history

## Version 1.0.0: initial freeze, 2026-09-12

Created 40 manually composed labels against the existing corpus with SHA-256 `d676b0a4872d627fa3a13b8d9ab7e8b87733b3e5dccff5efd914143a9a949371`. No corpus message or generated corpus metadata was edited. There was no prior evaluation ground truth and no retrieval engine or scoring output.

Initial drafting review, before freeze:

- Q004's query wording was simplified to an ordinary question about extra software on the panel's computer. Its target remained MSG_001154.
- Q017 was scoped to May after inspecting identical Software Engineering exam forwards on April 8, April 23 and May 23. Its intended target remained MSG_002058. The date restriction is visible in the query.
- The overlap convention conservatively retains `may` because it can name a calendar month, and removes duplicate function-word entries. No topic-specific stopwords were added; no labels were changed to improve retrieval results.

`freeze_manifest.json` records the final corpus, labels, overlap convention, implementation and review/history hashes. It is created only after validation and review. Normal validation checks these hashes and never rewrites labels or the manifest.

## Future corrections

A correction must document query IDs, previous and replacement wording/target/flag, the factual or ambiguity rationale, and reviewer/date. Preserve the previous manifest in version history, version the affected artifacts, review the hard subset again if affected, and rerun all affected baseline/hybrid comparisons using the same new version. Never change an expected answer solely because a system retrieved something else. No post-freeze corrections have occurred.
