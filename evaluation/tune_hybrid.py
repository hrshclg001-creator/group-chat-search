"""Measure a small, declared profile set without passing labels to retrieval.

Run from root: python -m evaluation.tune_hybrid
The script reports a winner but never edits ranking configuration or labels.
"""

from datetime import datetime, timezone
import json

from backend.app.search import load_corpus
from backend.app.search.hybrid import HybridSearch
from backend.app.search.ranking_config import PROFILES
from evaluation.evaluate import ROOT
from evaluation.metrics import summarize
from evaluation.validate_queries import CORPUS_PATH, METADATA_PATH, QUERY_PATH, MANIFEST_PATH, sha256, validate_files


def select_profile(trials):
    # Global Top-1 first; Recall@3 breaks ties, then original declaration order.
    return max(trials, key=lambda trial: (trial['metrics']['top1_accuracy']['correct'],
                                         trial['metrics']['recall_at_3']['correct']))['profile']


def main():
    validate_files()
    inputs = {str(path.relative_to(ROOT)).replace('\\', '/'): sha256(path)
              for path in (CORPUS_PATH, METADATA_PATH, QUERY_PATH, MANIFEST_PATH)}
    searcher = HybridSearch(load_corpus(CORPUS_PATH))
    queries = json.loads(QUERY_PATH.read_text(encoding='utf-8'))
    # Preparation sees text only; matrices/constraints are identical in trials.
    prepared = [searcher.prepare(item['query']) for item in queries]
    trials = []
    for name, config in PROFILES.items():
        rows = []
        for item, signals in zip(queries, prepared):
            hits = searcher.rank(signals, top_k=3, config=config)
            rows.append({**item, 'retrieved_ids': [hit.id for hit in hits]})
        trial = {'profile': name, 'configuration': config.to_dict(), 'metrics': summarize(rows), 'queries': rows}
        trials.append(trial)
        print(name, json.dumps(trial['metrics']), flush=True)
    validate_files()
    if any(sha256(ROOT / path) != digest for path, digest in inputs.items()):
        raise ValueError('Inputs changed during tuning')
    source_paths = list((ROOT / 'backend/app/search').glob('*.py')) + list((ROOT / 'backend/app/query_understanding').glob('*.py'))
    source_paths += [ROOT / 'evaluation/tune_hybrid.py', ROOT / 'evaluation/metrics.py']
    report = {
        'measured_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'selection_rule': 'Highest overall Top-1, then Recall@3, then declared profile order; no per-query/category tuning.',
        'selected_profile': select_profile(trials), 'input_sha256': inputs,
        'source_sha256': {str(path.relative_to(ROOT)).replace('\\', '/'): sha256(path) for path in sorted(source_paths)},
        'requirements_lock_sha256': sha256(ROOT / 'backend/requirements.lock.txt'),
        'index_configuration': searcher.configuration(),
        'limitations': 'The frozen 40 queries are also the tuning set; no independent test set was measured.',
        'trials': trials,
    }
    destination = ROOT / 'results/hybrid_tuning.json'
    destination.write_bytes((json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8'))
    print(f"Selected {report['selected_profile']}; saved {destination}")


if __name__ == '__main__':
    main()
