"""Exact-message-ID metrics, independent of the retrieval method."""


def rate(correct, total):
    return {'correct': correct, 'total': total,
            'value': correct / total if total else None,
            'percent': 100 * correct / total if total else None}


def summarize(rows):
    """Rows have expected_message_id, retrieved_ids, category and hard flag.

    Each query has exactly one labelled relevant message, so Recall@3 is the
    fraction of queries for which that message occurs in the first three hits.
    """
    if not rows:
        raise ValueError('Cannot score an empty evaluation set')

    def top1(row):
        return bool(row['retrieved_ids']) and row['retrieved_ids'][0] == row['expected_message_id']

    overall = rate(sum(top1(row) for row in rows), len(rows))
    hard_rows = [row for row in rows if row['zero_word_overlap']]
    hard = rate(sum(top1(row) for row in hard_rows), len(hard_rows))
    categories = {}
    for category in sorted({row['category'] for row in rows}):
        subset = [row for row in rows if row['category'] == category]
        categories[category] = rate(sum(top1(row) for row in subset), len(subset))
    return {
        'top1_accuracy': overall,
        'recall_at_3': rate(sum(row['expected_message_id'] in row['retrieved_ids'][:3]
                              for row in rows), len(rows)),
        'zero_word_overlap_top1_accuracy': hard,
        'top1_accuracy_by_category': categories,
        'overall_minus_hard_percentage_points':
            overall['percent'] - hard['percent'] if hard_rows else None,
    }
