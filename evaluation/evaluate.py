"""Run lexical, semantic, contextual or hybrid retrieval on frozen labels.

Usage from repository root: python evaluation/evaluate.py --all
Or: python evaluation/evaluate.py --method lexical
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
from evaluation.reporting import METHODS, failure_lines, terminal_table, write_comparison_artifacts
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


def run_method(method='lexical', encoder=None):
    validation = validate_files()  # Includes all frozen hashes; no --draft bypass.
    before = {path: sha256(path) for path in (CORPUS_PATH, METADATA_PATH, QUERY_PATH, MANIFEST_PATH)}
    messages = load_corpus(CORPUS_PATH)
    if method == 'lexical':
        searcher = LexicalSearch(messages)
    elif method in ('semantic', 'contextual'):
        from backend.app.search.semantic import SemanticSearch
        searcher = SemanticSearch(messages, contextual=method == 'contextual', encoder=encoder)
    elif method == 'hybrid':
        from backend.app.search.hybrid import HybridSearch
        searcher = HybridSearch(messages, encoder=encoder)
    else:
        raise ValueError(f'Unknown retrieval method: {method}')
    queries = json.loads(QUERY_PATH.read_text(encoding='utf-8'))
    rows = evaluate_queries(searcher, queries)
    if any(sha256(path) != digest for path, digest in before.items()):
        raise ValueError('Evaluation inputs changed during the benchmark')
    validate_files()
    source_paths = sorted((ROOT / 'backend/app/search').glob('*.py')) + [
        Path(__file__), ROOT / 'evaluation/metrics.py', ROOT / 'evaluation/validate_queries.py',
        ROOT / 'evaluation/reporting.py', ROOT / 'evaluation/compare.py',
    ]
    if method == 'hybrid':
        source_paths += sorted((ROOT / 'backend/app/query_understanding').glob('*.py'))
    return {
        'method': method, 'schema_version': '1.1.0',
        'measured_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'metrics': summarize(rows),
        'configuration': searcher.configuration(),
        'evaluation_top_k': 3,
        'corpus_message_count': len(messages),
        'query_count': validation['query_count'],
        'hard_query_count': validation['hard_query_count'],
        'reference_date': json.loads(METADATA_PATH.read_text(encoding='utf-8'))['reference_date'],
        'freeze_verified': True,
        'freeze_version': json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))['version'],
        'input_sha256': {str(path.relative_to(ROOT)).replace('\\', '/'): digest
                         for path, digest in before.items()},
        'source_sha256': {str(path.resolve().relative_to(ROOT)).replace('\\', '/'): sha256(path)
                          for path in source_paths},
        'requirements_lock_sha256': sha256(ROOT / 'backend/requirements.lock.txt'),
        'environment': {
            'python': platform.python_version(), 'platform': platform.platform(),
            'dependencies': {name: version(name) for name in (
                ('scikit-learn', 'numpy', 'scipy', 'joblib', 'threadpoolctl', 'sentence-transformers',
                 'transformers', 'torch', 'huggingface-hub') if method == 'hybrid' else
                ('scikit-learn', 'numpy', 'scipy', 'joblib', 'threadpoolctl') if method == 'lexical' else
                ('sentence-transformers', 'transformers', 'torch', 'numpy', 'huggingface-hub'))},
        },
        'limitations': ([
            'Hybrid profile selection used these same 40 labels; this is not held-out generalization accuracy.',
            'Rule-based sender/time interpretation can miss or misinterpret unsupported phrasing.',
            'Only exact current target IDs receive credit, never answers found solely in neighboring context.',
            'No external LLM, cross-encoder, query-specific answer rules or evaluation labels enter retrieval.',
        ] if method == 'hybrid' else [
            'No explicit sender/time ranking; only original text or bounded chronological context supplies features.',
            'Context can match a neighboring fact; only the anchored current message ID receives credit.',
            'Top-1 requires the exact labelled message, including when repeated background messages look equivalent.',
            'Fixed untuned configurations; surrounding messages can contain unrelated interruptions.',
        ]),
        'queries': rows,
    }, {message.id: message for message in messages}


def run_lexical():
    return run_method('lexical')


def print_report(report, messages):
    metrics = report['metrics']
    for label, key in [('Top-1 accuracy', 'top1_accuracy'), ('Recall@3', 'recall_at_3'),
                       ('Zero-overlap Top-1', 'zero_word_overlap_top1_accuracy')]:
        item = metrics[key]
        print(f"{label}: {item['correct']}/{item['total']} ({item['percent']:.2f}%)")
    print(f"Overall minus hard: {metrics['overall_minus_hard_percentage_points']:+.2f} percentage points")
    for category, item in metrics['top1_accuracy_by_category'].items():
        print(f"{category} Top-1: {item['correct']}/{item['total']} ({item['percent']:.2f}%)")
    print('\n'.join(failure_lines(report, messages)))


def run_all(directory=ROOT / 'results'):
    validate_files()
    reports = {}
    encoder = None
    for index, method in enumerate(METHODS, 1):
        print(f'[{index}/{len(METHODS)}] Evaluating {method}...', flush=True)
        if method != 'lexical' and encoder is None:
            from backend.app.search.embedding import LocalEncoder
            encoder = LocalEncoder()
        report, messages = run_method(method, encoder=encoder)
        reports[method] = report
    validate_files()
    # Cross-method validation prevents mixing inputs even if files changed
    # between individual method runs. No weight tuning happens here.
    write_comparison_artifacts(reports, messages, directory)
    print('\n' + terminal_table(reports))
    print('\nHard-N is the full zero-word-overlap subset. Cells show percent (correct/total).')
    print('Gap = overall Top-1 minus hard Top-1, in percentage points.')
    for method in METHODS:
        print(f'\n=== {method.upper()} FAILED QUERIES ===')
        print('\n'.join(failure_lines(reports[method], messages)))
    # Repeat the compact table after diagnostics so it remains easy to find.
    print('\n' + terminal_table(reports))
    print(f'\nSaved all measured reports, comparison.csv, benchmark.png, failed_queries.txt and evaluation_summary.md to {directory}')
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--method', choices=METHODS)
    selection.add_argument('--all', action='store_true', help='Run all four methods and generate comparison artifacts')
    args = parser.parse_args()
    # Preserve emojis in redirected logs; avoid Windows console encoding crashes.
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        if args.all:
            run_all()
            return
        report, messages = run_method(args.method)
    except (ValueError, OSError, ImportError) as exc:
        parser.exit(1, f'Benchmark failed: {exc}\n')
    destination = ROOT / 'results' / f'{args.method}.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes((json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8'))
    print_report(report, messages)
    print(f'\nSaved measured results to {destination}')


if __name__ == '__main__':
    main()
