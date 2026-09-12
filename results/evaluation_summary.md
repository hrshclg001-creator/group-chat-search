# Retrieval evaluation

Automatically generated at 2026-09-12T08:31:46+00:00.

All four methods were run on the same frozen 40 queries and 4,634 synthetic messages. Reference date: 2026-09-01. **Hard-10** means the complete zero-meaningful-word-overlap subset; it is not restricted to eight queries.

| Method | Top-1 | Recall@3 | Hard-10 | Person | Time | Semantic | Gap (pp) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Lexical | 22.5% (9/40) | 40.0% (16/40) | 0.0% (0/10) | 30.0% (3/10) | 30.0% (3/10) | 15.0% (3/20) | +22.5 |
| Semantic | 32.5% (13/40) | 40.0% (16/40) | 10.0% (1/10) | 30.0% (3/10) | 40.0% (4/10) | 30.0% (6/20) | +22.5 |
| Contextual | 10.0% (4/40) | 30.0% (12/40) | 10.0% (1/10) | 10.0% (1/10) | 20.0% (2/10) | 5.0% (1/20) | +0.0 |
| Hybrid | 55.0% (22/40) | 62.5% (25/40) | 10.0% (1/10) | 70.0% (7/10) | 80.0% (8/10) | 35.0% (7/20) | +45.0 |

Every accuracy cell includes correct/total. Gap is overall Top-1 minus hard Top-1, in signed percentage points. Only the exact matching message ID receives credit; neighboring answers do not.

Highest measured overall Top-1: **Hybrid**, 55.0% (22/40).

Top-1 failures by method: lexical 31, semantic 27, contextual 36, hybrid 18. Expected original messages, all top-three retrieved messages and available score components are in [failed_queries.txt](failed_queries.txt).

**Limitations:** Hybrid weights were selected on this same query set, so these are development-set results, not held-out generalization accuracy. Zero-overlap questions can remain difficult even when person/time retrieval improves. No labels or ranking settings were changed by this run.

Reproduce from the repository root after installing the locked backend dependencies and preparing the local model:

```text
python evaluation/evaluate.py --all
```

Artifacts: [CSV](comparison.csv), [comparison JSON](comparison.json), [chart](benchmark.png), [lexical](lexical.json), [semantic](semantic.json), [contextual](contextual.json), [hybrid](hybrid.json). Per-method JSON records model/dependency versions, configuration, source/input hashes and rankings. Comparison JSON records reporting versions and artifact hashes.
