"""Run the lexical baseline against the frozen evaluation set.

Usage from repository root: python evaluation/evaluate.py --method lexical
"""

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

# Support the requested direct-script command as well as `-m evaluation.evaluate`.
ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ''):
    sys.path.insert(0, str(ROOT))

from backend.app.search import LexicalSearch, load_corpus
from evaluation.metrics import summarize
from evaluation.validate_queries import (
    CORPUS_PATH, MANIFEST_PATH, METADATA_PATH, QUERY_PATH, sha256, validate_files,
)


def evaluate_queries(searcher, queries):
    rows = []
    for item in queries:
        # Only query text and a fixed K enter retrieval, never target/category/flag/notes.
        hits = searcher.search(item['query'], top_k=3)
        ids = [hit.id for hit in hits]
        rows.append({
            'id': item['id'], 'query': item['query'], 'category': item['category'],
            'zero_word_overlap': item['zero_word_overlap'],
            'expected_message_id': item['expected_message_id'],
            'retrieved_ids': ids,
            'top1_correct': bool(ids) and ids[0] == item['expected_message_id'],
            'recalled_at_3': item['expected_message_id'] in ids,
            'retrieved_messages': [hit.to_dict() for hit in hits],
        })
    return rows


def run_lexical():
    validation = validate_files()  # Includes all frozen hashes; no --draft bypass.
    before = {path: sha256(path) for path in (CORPUS_PATH, METADATA_PATH, QUERY_PATH, MANIFEST_PATH)}
    messages = load_corpus(CORPUS_PATH)
    searcher = LexicalSearch(messages)
    queries = json.loads(QUERY_PATH.read_text(encoding='utf-8'))
    rows = evaluate_queries(searcher, queries)
    if any(sha256(path) != digest for path, digest in before.items()):
        raise ValueError('Evaluation inputs changed during the benchmark')
    validate_files()
    source_paths = sorted((ROOT / 'backend/app/search').glob('*.py')) + [
        Path(__file__), ROOT / 'evaluation/metrics.py', ROOT / 'evaluation/validate_queries.py',
    ]
    return {
        'method': 'lexical', 'schema_version': '1.0.0',
        'measured_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'metrics': summarize(rows),
        'configuration': searcher.configuration(),
        'evaluation_top_k': 3,
        'corpus_message_count': len(messages),
        'query_count': validation['query_count'],
        'hard_query_count': validation['hard_query_count'],
        'reference_date': '2026-09-01',
        'freeze_verified': True,
        'freeze_version': json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))['version'],
        'input_sha256': {str(path.relative_to(ROOT)).replace('\\', '/'): digest
                         for path, digest in before.items()},
        'source_sha256': {str(path.resolve().relative_to(ROOT)).replace('\\', '/'): sha256(path)
                          for path in source_paths},
        'requirements_lock_sha256': sha256(ROOT / 'backend/requirements.lock.txt'),
        'environment': {
            'python': platform.python_version(), 'platform': platform.platform(),
            'dependencies': {name: version(name) for name in ('scikit-learn', 'numpy', 'scipy', 'joblib', 'threadpoolctl')},
        },
        'limitations': [
            'Message text only: no sender/time ranking, context expansion, embeddings or synonym understanding.',
            'Character overlap may give nonzero scores even for the frozen zero-word-overlap subset.',
            'Top-1 requires the exact labelled message, including when repeated background messages look equivalent.',
            'One fixed untuned lexical configuration; semantic and hybrid baselines are not measured.',
        ],
        'queries': rows,
    }, {message.id: message for message in messages}


def print_report(report, messages):
    metrics = report['metrics']
    for label, key in [('Top-1 accuracy', 'top1_accuracy'), ('Recall@3', 'recall_at_3'),
                       ('Zero-overlap Top-1', 'zero_word_overlap_top1_accuracy')]:
        item = metrics[key]
        print(f"{label}: {item['correct']}/{item['total']} ({item['percent']:.2f}%)")
    print(f"Overall minus hard: {metrics['overall_minus_hard_percentage_points']:+.2f} percentage points")
    for category, item in metrics['top1_accuracy_by_category'].items():
        print(f"{category} Top-1: {item['correct']}/{item['total']} ({item['percent']:.2f}%)")
    for row in report['queries']:
        if row['top1_correct']:
            continue
        expected = messages[row['expected_message_id']]
        print(f"\nINCORRECT {row['id']} [{row['category']}] {row['query']}")
        print(f'  Expected {expected.id} | {expected.sender} | {expected.timestamp} | {expected.text}')
        if row['retrieved_messages']:
            hit = row['retrieved_messages'][0]
            print(f"  Retrieved {hit['id']} | score={hit['lexical_score']:.6f} | {hit['sender']} | {hit['timestamp']} | {hit['text']}")
        else:
            print('  Retrieved: no positive-scoring message')
        print(f"  Top 3: {', '.join(row['retrieved_ids']) or '(empty)'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--method', required=True, choices=['lexical'])
    args = parser.parse_args()
    # Preserve emojis in redirected logs; avoid Windows console encoding crashes.
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        report, messages = run_lexical()
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Benchmark failed: {exc}\n')
    destination = ROOT / 'results' / f'{args.method}.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes((json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8'))
    print_report(report, messages)
    print(f'\nSaved measured results to {destination}')


if __name__ == '__main__':
    main()
