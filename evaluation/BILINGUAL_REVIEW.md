# Supplemental bilingual evaluation

Authored before reranker implementation or scoring on 2026-09-12. This file and `bilingual_queries.json` supplement, rather than replace, the original frozen 40-query assessment.

The 24 manually composed queries form 12 English/Hinglish pairs with identical intended facts and target IDs. Targets were read from the existing corpus and do not repeat the original benchmark's targets. Categories: eight semantic, eight person, eight time. Query language is explicitly labelled. `zero_word_overlap: false` means no hard-subset claim is made for this set.

Each pair's notes explain the answer-bearing message. Dates disambiguate repeated background templates. Cafe cost is explicitly separated from total event cost; the administration-interface question asks for the initial framework proposal, not the final stack. IDs and target texts are checked before evaluation. Neither query labels nor corpus authoring annotations enter retrieval.

This is supplemental development evidence, not independent human annotation or a held-out generalization estimate: some questions share known decision threads, and the author has inspected prior failures. Pairing also means 24 queries measure only 12 distinct facts. Future independent evaluation should split whole threads/topics before tuning.

Predeclared experiment: use one pinned multilingual mMARCO cross-encoder on the union of the top 128 eligible results from each of original semantic, contextual semantic, lexical and first-stage hybrid scoring. Rerank original message text (with legitimate sender/date metadata), without appending neighboring answers. Combine 85% cross-encoder sigmoid score with 15% first-stage hybrid score. No weight sweep, query-specific translation list or answer-stage exceptions. Assess all four original methods and this candidate, candidate recall, latency, language/category results and the unchanged hard subset. Retain only a material aggregate gain with disclosed regressions.
