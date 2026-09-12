"""Supplemental paired queries retain a separate immutable identity."""

import json

from evaluation.evaluate_bilingual import ROOT, load_queries, measure


def test_bilingual_freeze_and_pair_balance():
    queries, _ = load_queries()
    assert len(queries) == 24
    assert sum(q['language'] == 'hinglish' for q in queries) == 12
    assert len({q['expected_message_id'] for q in queries}) == 12
    original = json.loads((ROOT / 'evaluation/queries.json').read_text(encoding='utf-8'))
    assert not ({q['expected_message_id'] for q in queries} & {q['expected_message_id'] for q in original})


def test_supplemental_evaluation_passes_only_query_and_k():
    class Spy:
        def search(self, query, top_k):
            assert query == 'Where is the room?' and top_k == 3
            return []

        def configuration(self):
            return {}

    query = {'id': 'B001', 'query': 'Where is the room?', 'expected_message_id': 'SECRET_LABEL',
             'category': 'semantic', 'language': 'hinglish', 'zero_word_overlap': False}
    result = measure(Spy(), [query])
    assert result['metrics']['top1_accuracy']['correct'] == 0
    assert result['by_language']['hinglish']['top1_accuracy']['total'] == 1
