"""Evaluation passes no labels to retrieval and preserves actual hit identities."""

import copy

from backend.app.search import SearchResult
from evaluation.evaluate import evaluate_queries, print_report
from evaluation.metrics import summarize


def test_evaluator_passes_only_query_text_and_fixed_k(capsys):
    class SearchSpy:
        def search(self, *args, **kwargs):
            assert args == ('plain query',)
            assert kwargs == {'top_k': 3}
            return [SearchResult('MSG_000002', 'Fictional Student', '2026-03-01T10:00:00+05:30',
                                 'actual retrieved message', .4)]

    queries = [{'id': 'Q001', 'query': 'plain query', 'expected_message_id': 'MSG_000001',
                'category': 'semantic', 'zero_word_overlap': True, 'notes': 'Must never enter retrieval'}]
    before = copy.deepcopy(queries)
    rows = evaluate_queries(SearchSpy(), queries)
    assert queries == before
    assert rows[0]['retrieved_ids'] == ['MSG_000002']
    assert rows[0]['top1_correct'] is False
    assert rows[0]['recalled_at_3'] is False
    assert rows[0]['retrieved_messages'][0]['text'] == 'actual retrieved message'
    expected = SearchResult('MSG_000001', 'Other Student', '2026-03-01T09:00:00+05:30', 'intended message', 0)
    print_report({'queries': rows, 'metrics': summarize(rows)}, {'MSG_000001': expected})
    output = capsys.readouterr().out
    assert 'INCORRECT Q001' in output
    assert 'Expected MSG_000001' in output
    assert 'Retrieved MSG_000002' in output
    assert 'actual retrieved message' in output


def test_expected_id_in_context_is_not_counted_as_a_correct_current_hit():
    from backend.app.search.semantic import SemanticResult

    class NeighborSpy:
        def search(self, query, top_k):
            return [SemanticResult('MSG_000002', 'Student', '2026-03-01T10:00:00+05:30',
                                   'done', 'done', .9, 'Previous: answer\nCurrent: done',
                                   ('MSG_000001', 'MSG_000002'), (), 'context embedding', ())]

    rows = evaluate_queries(NeighborSpy(), [{'id': 'Q001', 'query': 'question',
        'expected_message_id': 'MSG_000001', 'category': 'semantic', 'zero_word_overlap': True}])
    assert rows[0]['top1_correct'] is False
    assert rows[0]['recalled_at_3'] is False
