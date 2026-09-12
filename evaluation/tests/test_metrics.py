"""Known rankings test denominators, top-three boundaries and signed gaps."""

import pytest

from evaluation.metrics import summarize


def row(expected, retrieved, category='semantic', hard=False):
    return {'expected_message_id': expected, 'retrieved_ids': retrieved,
            'category': category, 'zero_word_overlap': hard}


def test_known_rankings_and_category_denominators():
    result = summarize([
        row('a', ['a', 'x'], hard=True),
        row('b', ['x', 'y', 'b'], 'person'),
        row('c', [], 'time'),
        row('d', ['x', 'y', 'z', 'd'], hard=True),
    ])
    assert result['top1_accuracy'] == {'correct': 1, 'total': 4, 'value': .25, 'percent': 25.0}
    assert result['recall_at_3']['correct'] == 2
    assert result['recall_at_3']['total'] == 4
    assert result['zero_word_overlap_top1_accuracy']['value'] == .5
    assert result['overall_minus_hard_percentage_points'] == -25.0
    assert result['top1_accuracy_by_category']['semantic']['total'] == 2
    assert result['top1_accuracy_by_category']['person']['correct'] == 0
    assert result['top1_accuracy_by_category']['time']['total'] == 1


def test_missing_hard_subset_has_no_fabricated_accuracy():
    result = summarize([row('a', ['a'])])
    assert result['zero_word_overlap_top1_accuracy']['total'] == 0
    assert result['zero_word_overlap_top1_accuracy']['value'] is None
    assert result['overall_minus_hard_percentage_points'] is None


def test_duplicate_retrievals_do_not_inflate_recall_and_neighbor_is_wrong():
    result = summarize([row('a', ['x', 'a', 'a']), row('b', ['neighbor_of_b'])])
    assert result['recall_at_3']['correct'] == 1
    assert result['top1_accuracy']['correct'] == 0


def test_empty_evaluation_fails():
    with pytest.raises(ValueError, match='empty'):
        summarize([])
