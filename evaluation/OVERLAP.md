# Word-overlap convention (version 1.0.0)

This convention is documented before labelling checks or retrieval scoring. The complete fixed stopword list is in `overlap_convention.json`; it consists of English and Romanized Hindi grammatical/function words. It is not learned from the corpus and contains no topic-specific exclusions.

1. Compare the user's `query` with the referenced message's **text**. Sender names, timestamps, IDs, notes, thread metadata and surrounding messages are not appended. Names or dates actually written in either text remain content tokens. This is text-only lexical disjointness, not a claim that person/time metadata supplies no clues.
2. Apply Unicode NFKC and casefold. Normalize curly apostrophes; expand `can't` to `can not`, `won't` to `will not`, other `n't` endings to ` not`, and common auxiliary suffixes (`'ll`, `'re`, `'ve`, `'m`, `'d`). Remove possessive `'s`.
3. Tokenize runs of Unicode letters or digits. Punctuation, underscores, emoji and brackets are separators. Thus hyphenated expressions split into words; `[PDF]` retains `pdf`; URLs retain their letter/digit components; numbers and dates remain tokens.
4. Remove only the explicit function-word list. Keep negation (`no`, `not`, `nahi`, `mat`), quantities, names, places, technology names, time words (`last`, `month`, `yesterday`), and ordinary content words. Retain `may` even when it is an auxiliary, because it is also a month name; the conservative rule avoids removing calendar information after casefolding.
5. Use sets, with no stemming, lemmatization, translation, spelling correction or synonym expansion. A query is zero-overlap exactly when both content sets are nonempty and their intersection is empty. The flag must agree with this result for **every** query, including those marked false.

Manual hard-subset review must additionally establish a meaningful semantic relationship and a defensible target in its conversational context. A mere inflection, misspelling, obscure synonym, empty query or emoji is not sufficient evidence of a good semantic test. The hard queries should ask ordinary archive questions; terms such as nausea/motion sickness and dorm lounge/hostel common room are substantive paraphrases.

The overlap checker validates labels only. It does not retrieve, rank, embed or score messages. No stopwords may be added to rescue a particular label after freezing. A justified convention change requires a new version, a change-history entry, a renewed review and rerunning all affected future comparisons.
