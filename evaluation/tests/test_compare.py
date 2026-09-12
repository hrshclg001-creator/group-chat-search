import pytest

from evaluation.compare import compare_reports
from evaluation.metrics import summarize


def report(correct, method):
    rows = [{'id': 'Q001', 'expected_message_id': 'a', 'retrieved_ids': ['a' if correct else 'b'],
             'top1_correct': correct, 'zero_word_overlap': True, 'category': 'semantic'}]
    return {'method': method, 'input_sha256': {'queries': 'unchanged'},
            'queries': rows, 'metrics': summarize(rows)}


def test_category_comparison_reports_losses_as_well_as_gains():
    result = compare_reports(report(True, 'semantic'), report(False, 'contextual'))
    assert result['category_changes']['semantic']['direction'] == 'worse'
    assert result['category_changes']['semantic']['delta_percentage_points'] == -100
    assert result['newly_incorrect_queries'] == ['Q001']
    reverse = compare_reports(report(False, 'semantic'), report(True, 'contextual'))
    assert reverse['newly_correct_queries'] == ['Q001']


def test_comparison_refuses_different_labels():
    first, second = report(True, 'semantic'), report(False, 'contextual')
    second['input_sha256']['queries'] = 'changed'
    with pytest.raises(ValueError, match='different frozen inputs'):
        compare_reports(first, second)
