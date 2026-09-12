# General retrieval tuning

Read AGENTS.md and inspected all 19 initial hybrid errors before changing code. The 40 labels, expected IDs, corpus, overlap convention and freeze manifest are unchanged. The hard subset is **10** queries. Detailed evidence and recommendations: [failure_analysis.md](failure_analysis.md).

| Change | Before Top-1 | After Top-1 | Recall@3 before → after | Hard Top-1 before → after | Decision |
| --- | --- | --- | --- | --- | --- |
| Remove confidently resolved sender/chat-date spans from similarity text; retain filters and event dates | 21/40 (52.5%) | 20/40 (50%) | 25/40 → 27/40 | 1/10 (10%) → 1/10 (10%) | Rejected: one gain, two losses |
| Revert metadata-text removal; rerun all four methods | 20/40 (50%) | 21/40 (52.5%) | 27/40 → 25/40 | 1/10 (10%) → 1/10 (10%) | Baseline restored |
| Require the current message's stored type for explicit forwarded-item/attachment requests; intersect author/date constraints | 21/40 (52.5%) | 22/40 (55%) | 25/40 → 25/40 | 1/10 (10%) → 1/10 (10%) | Retained: one gain, no Top-1 losses |

Metadata-text removal gained Q027 but lost Q014 and Q040. Person accuracy moved 7/10 → 8/10, time 7/10 → 6/10, semantic 7/20 → 6/20. Its better Recall@3 does not compensate for the Top-1 regressions. No selective exceptions were added to rescue individual queries.

The retained type constraint fixes Q038: the actual forwarded warning replaces a reminder that merely mentions a notice. Time accuracy is now 8/10 (80%); person remains 7/10 (70%) and semantic 7/20 (35%). Rules also support explicit PDF, image, voice-message and URL requests on independent fixtures. They use stored message types, not topic/episode/thread annotations, message IDs or target text. Negated, alternative and mention/discussion requests are left unconstrained. An empty type/author/date intersection returns no results. Effective `message_type` is exposed in API query metadata.

Final overall-minus-hard gap: **55% (22/40) − 10% (1/10) = +45 percentage points**, versus +42.5 pp initially. The gap widened; this is **not a hard-semantic improvement**. Nine hard queries still fail. Baseline Top-1 remains lexical 9/40, semantic 13/40 and contextual 4/40; all their top-three rankings are unchanged.

## Reproduction and evidence

Each meaningful change, including the revert, was followed by the complete `python evaluation/evaluate.py --all` run, using the installed `backend/.venv` interpreter, cached pinned local model and unchanged frozen inputs. No weight, model, token-budget, context-window or dependency change was retained.

- Initial reports: [tuning/before](tuning/before/). Pre-tuning source commit: `4767a058786a534c4dbb1dc0c99d50397aa57898`.
- Rejected experiment, full four-method reports and exact patch: [tuning/metadata_separation](tuning/metadata_separation/). The patch applies to the pre-tuning source; use a separate checkout to reproduce it, not the final message-type implementation. The archived comparison records all metrics and source/input hashes.
- Complete revert output: [tuning/revert_output.txt](tuning/revert_output.txt).
- Retained result: [hybrid.json](hybrid.json), [comparison.csv](comparison.csv), [benchmark.png](benchmark.png), [evaluation_summary.md](evaluation_summary.md). Reproduce from the final source with the command above.
- Checks: **206 backend tests and 40 evaluation tests passed (246 total)**. Initial type-field contract assertions were updated for the intentional loader change; the complete suite then passed. The rejected experiment's focused tests passed 41/41 before evaluation. Frozen-input, current source, archived/current artifact hashes and recomputed aggregates were verified. Only Q038 changed Top-1 correctness in the retained version. Existing tokenizer-length and upstream matplotlib/pyparsing warnings remain nonblocking. No frontend files changed; frontend checks were not rerun.

## Stop decision

Two general candidates were tested; no weight sweep or further failure-specific rules were attempted. Remaining problems need better mixed-language/answer-stage semantics and reliable current-message anchoring. Recommend a local answer-aware reranker with measured candidate recall, bounded topic-consistent context selection, and evaluation on independently labelled data. These are recommendations, not measured improvements.

Further tuning on these same 40 questions would risk selecting linguistic exceptions, synonym lists or context settings around known answers. Keep this historical set frozen, group repeated targets and related episodes when splitting new data, and obtain a separate development/held-out set before more optimization. The current result is development-set performance, not evidence of held-out generalization. No ground-truth target was demonstrably invalid, and none was edited.
