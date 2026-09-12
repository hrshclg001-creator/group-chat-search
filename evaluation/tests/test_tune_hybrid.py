from evaluation.tune_hybrid import select_profile


def trial(name, top1, recall):
    return {'profile': name, 'metrics': {'top1_accuracy': {'correct': top1},
                                        'recall_at_3': {'correct': recall}}}


def test_selection_uses_aggregate_top1_then_recall_then_declared_order():
    assert select_profile([trial('first', 3, 5), trial('second', 4, 4)]) == 'second'
    assert select_profile([trial('first', 4, 5), trial('second', 4, 6)]) == 'second'
    assert select_profile([trial('first', 4, 6), trial('second', 4, 6)]) == 'first'
