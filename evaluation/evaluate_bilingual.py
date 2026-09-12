"""Compare first-stage and reranked retrieval on frozen English/Hinglish pairs.

Run from root: python -m evaluation.evaluate_bilingual
This supplement never replaces the original 40-query assessment.
"""

import hashlib
import argparse
import json
from pathlib import Path
from time import perf_counter

from backend.app.search.corpus import load_corpus
from backend.app.search.embedding import LocalEncoder
from backend.app.search.hybrid import HybridSearch
from backend.app.search.reranked import RerankedSearch
from evaluation.metrics import summarize
from evaluation.validate_queries import validate_files

ROOT = Path(__file__).resolve().parents[1]


def load_queries():
    validate_files()  # Also freezes participant metadata and reference date.
    manifest = json.loads((ROOT / 'evaluation/bilingual_freeze.json').read_text(encoding='utf-8'))
    required = {'evaluation/bilingual_queries.json', 'evaluation/BILINGUAL_REVIEW.md', 'backend/data/messages.jsonl'}
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ValueError('Bilingual freeze manifest must cover the declared inputs')
    for name, expected in manifest.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Frozen bilingual input changed: {name}')
    queries = json.loads((ROOT / 'evaluation/bilingual_queries.json').read_text(encoding='utf-8'))
    targets = {row.id for row in load_corpus()}
    if len(queries) != 24 or len({q['id'] for q in queries}) != 24:
        raise ValueError('Expected 24 unique bilingual queries')
    for q in queries:
        if q['expected_message_id'] not in targets or q['language'] not in ('english', 'hinglish'):
            raise ValueError('Invalid bilingual target or language')
    pairs = {q['pair_id'] for q in queries}
    for pair in pairs:
        rows = [q for q in queries if q['pair_id'] == pair]
        if len(rows) != 2 or {q['language'] for q in rows} != {'english', 'hinglish'} or len({q['expected_message_id'] for q in rows}) != 1:
            raise ValueError('Each pair requires equivalent English/Hinglish targets')
    return queries, manifest


def measure(engine, queries):
    rows = []
    for q in queries:
        started = perf_counter()
        hits = engine.search(q['query'], top_k=3)
        ids = [hit.id for hit in hits]
        row = {**q, 'retrieved_ids': ids, 'top1_correct': bool(ids) and ids[0] == q['expected_message_id'],
               'recalled_at_3': q['expected_message_id'] in ids,
               'search_time_ms': round((perf_counter() - started) * 1000, 3),
               'retrieved_messages': [hit.to_dict() for hit in hits]}
        if hasattr(engine, 'last_candidate_ids'):
            row['candidate_count'] = len(engine.last_candidate_ids)
            row['target_in_candidates'] = q['expected_message_id'] in engine.last_candidate_ids
        rows.append(row)
        print(f"{q['id']} {'PASS' if row['top1_correct'] else 'MISS'} {row['search_time_ms']:.0f}ms", flush=True)
    return {'metrics': summarize(rows), 'by_language': {
        language: summarize([row for row in rows if row.get('language') == language])
        for language in ('english', 'hinglish') if any(row.get('language') == language for row in rows)},
        'configuration': engine.configuration(), 'queries': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--method', choices=('first_stage', 'reranked', 'both'), default='both')
    args = parser.parse_args()
    queries, manifest = load_queries()
    encoder = LocalEncoder()
    messages = load_corpus()
    reports = {}
    for name, cls in [('first_stage', HybridSearch), ('reranked', RerankedSearch)]:
        if args.method not in ('both', name):
            continue
        print(name, flush=True)
        engine = cls(messages, encoder=encoder)
        reports[name] = measure(engine, queries)
        del engine
    load_queries()
    report = {'input_sha256': manifest, 'limitations': 'Supplemental development pairs, not independent held-out data.',
              'reports': reports}
    destination = ROOT / ('results/bilingual.json' if args.method == 'both' else f'results/bilingual_{args.method}.json')
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for name, result in reports.items():
        print(name, result['metrics']['top1_accuracy'],
              {lang: metrics['top1_accuracy'] for lang, metrics in result['by_language'].items()}, flush=True)


if __name__ == '__main__':
    main()
