"""Validate frozen retrieval labels without implementing or running retrieval.

From repository root: backend/.venv/Scripts/python.exe -m evaluation.validate_queries
"""

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from .overlap import content_words, overlap_details

ROOT = Path(__file__).resolve().parents[1]
QUERY_PATH = ROOT / 'evaluation' / 'queries.json'
CORPUS_PATH = ROOT / 'backend' / 'data' / 'messages.jsonl'
METADATA_PATH = CORPUS_PATH.with_name('corpus_metadata.json')
MANIFEST_PATH = QUERY_PATH.with_name('freeze_manifest.json')
CATEGORIES = {'semantic', 'person', 'time'}
FIELDS = {'id', 'query', 'expected_message_id', 'category', 'zero_word_overlap', 'notes'}
FROZEN_PATHS = {
    'backend/data/messages.jsonl', 'backend/data/corpus_metadata.json',
    'evaluation/queries.json', 'evaluation/overlap_convention.json',
    'evaluation/overlap.py', 'evaluation/OVERLAP.md',
    'evaluation/HARD_SUBSET_REVIEW.md', 'evaluation/label_changes.md',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_queries(queries, messages):
    require(isinstance(queries, list) and len(queries) == 40, 'Expected exactly 40 queries')
    require(isinstance(messages, list) and bool(messages), 'Corpus must be a nonempty list')
    by_id = {row['id']: row for row in messages}
    require(len(by_id) == len(messages), 'Duplicate corpus message IDs')
    for index, item in enumerate(queries, 1):
        require(isinstance(item, dict) and set(item) == FIELDS, f'Query {index}: expected exactly the required fields')
        require(item['id'] == f'Q{index:03d}', 'IDs must be unique and ordered Q001 through Q040')
        for field in ('query', 'expected_message_id', 'category', 'notes'):
            require(isinstance(item[field], str) and bool(item[field].strip()), f"{item['id']}: {field} must be nonempty text")
        require(re.fullmatch(r'MSG_\d{6}', item['expected_message_id']) is not None, 'Invalid target ID format')
        require(item['expected_message_id'] in by_id, f"{item['id']}: target ID does not exist")
        require(item['category'] in CATEGORIES, 'Unknown query category')
        require(type(item['zero_word_overlap']) is bool, 'zero_word_overlap must be a JSON boolean')
        require(bool(content_words(item['query'])), 'Query must contain meaningful content words')
    require(len({item['query'].strip().casefold() for item in queries}) == 40, 'Duplicate query text')
    counts = dict(sorted(Counter(item['category'] for item in queries).items()))
    require(set(counts) == CATEGORIES, 'All three required categories must exist')
    hard_ids = [item['id'] for item in queries if item['zero_word_overlap']]
    require(len(hard_ids) >= 8, 'Expected at least 8 marked zero_word_overlap queries')
    audits = []
    for item in queries:
        target = by_id[item['expected_message_id']]
        details = overlap_details(item['query'], target['text'])
        require(bool(details['target_content_words']), 'Target must contain meaningful content words')
        require(item['zero_word_overlap'] == details['zero_word_overlap'],
                f"{item['id']}: zero_word_overlap flag mismatch; shared={details['shared_content_words']}")
        audits.append({'id': item['id'], 'target_id': target['id'], **details})
    return {
        'query_count': len(queries),
        'category_counts': counts,
        'hard_query_count': len(hard_ids),
        'hard_query_ids': hard_ids,
        'distinct_target_count': len({item['expected_message_id'] for item in queries}),
        'decision_thread_ids_covered': sorted({by_id[item['expected_message_id']].get('thread_id')
                                              for item in queries
                                              if by_id[item['expected_message_id']].get('thread_id')}),
        'overlap_audit': audits,
    }


def validate_freeze(manifest, report, root=ROOT):
    require(manifest.get('status') == 'frozen', 'Evaluation set is not frozen')
    require(manifest.get('reference_date') == '2026-09-01', 'Frozen reference date mismatch')
    require(set(manifest.get('sha256', {})) == FROZEN_PATHS, 'Frozen file inventory mismatch')
    for relative_path, expected_hash in manifest['sha256'].items():
        require(sha256(root / relative_path) == expected_hash,
                f'Frozen hash mismatch: {relative_path}; document any legitimate correction before refreezing')
    for key in ('query_count', 'category_counts', 'hard_query_count', 'hard_query_ids', 'distinct_target_count'):
        require(manifest.get(key) == report[key], f'Frozen {key} mismatch')
    require(manifest.get('retrieval_scored') is False, 'Initial freeze must precede retrieval scoring')


def validate_files(draft=False):
    queries = json.loads(QUERY_PATH.read_text(encoding='utf-8'))
    messages = [json.loads(line) for line in CORPUS_PATH.read_text(encoding='utf-8').splitlines()]
    metadata = json.loads(METADATA_PATH.read_text(encoding='utf-8'))
    require(sha256(CORPUS_PATH) == metadata['sha256'], 'Corpus hash differs from generation metadata')
    require(metadata['reference_date'] == '2026-09-01', 'Corpus reference date mismatch')
    report = validate_queries(queries, messages)
    if not draft:
        require(MANIFEST_PATH.is_file(), 'Missing freeze manifest; use --draft only for pre-freeze review')
        validate_freeze(json.loads(MANIFEST_PATH.read_text(encoding='utf-8')), report)
    report['freeze_verified'] = not draft
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true', help='Validate labels before initial freeze; skips freeze checks')
    parser.add_argument('--show-overlap', action='store_true', help='Print token audit for every query')
    args = parser.parse_args()
    try:
        report = validate_files(draft=args.draft)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'Validation failed: {exc}\n')
    if not args.show_overlap:
        del report['overlap_audit']
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
