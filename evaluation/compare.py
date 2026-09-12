"""Compare measured runs only when they use identical frozen inputs."""

import json
from pathlib import Path

from .metrics import summarize

ROOT = Path(__file__).resolve().parents[1]


def compare_reports(baseline, candidate):
    if baseline['input_sha256'] != candidate['input_sha256']:
        raise ValueError('Cannot compare different frozen inputs')
    before = {row['id']: row for row in baseline['queries']}
    after = {row['id']: row for row in candidate['queries']}
    if set(before) != set(after) or any(before[key]['expected_message_id'] != after[key]['expected_message_id'] for key in before):
        raise ValueError('Cannot compare different query targets')
    old = summarize(baseline['queries'])
    new = summarize(candidate['queries'])
    if old != baseline['metrics'] or new != candidate['metrics']:
        raise ValueError('Saved aggregate metrics disagree with rankings')
    deltas = {}
    for category in old['top1_accuracy_by_category']:
        left = old['top1_accuracy_by_category'][category]
        right = new['top1_accuracy_by_category'][category]
        delta = right['percent'] - left['percent']
        deltas[category] = {'baseline': left, 'candidate': right, 'delta_percentage_points': delta,
                            'direction': 'improved' if delta > 0 else 'worse' if delta < 0 else 'unchanged'}
    return {
        'baseline_method': baseline['method'], 'candidate_method': candidate['method'],
        'top1_delta_percentage_points': new['top1_accuracy']['percent'] - old['top1_accuracy']['percent'],
        'recall_at_3_delta_percentage_points': new['recall_at_3']['percent'] - old['recall_at_3']['percent'],
        'hard_top1_delta_percentage_points': new['zero_word_overlap_top1_accuracy']['percent'] - old['zero_word_overlap_top1_accuracy']['percent'],
        'category_changes': deltas,
        'newly_correct_queries': [key for key in before if not before[key]['top1_correct'] and after[key]['top1_correct']],
        'newly_incorrect_queries': [key for key in before if before[key]['top1_correct'] and not after[key]['top1_correct']],
    }


def main():
    reports = {method: json.loads((ROOT / f'results/{method}.json').read_text(encoding='utf-8'))
               for method in ('lexical', 'semantic', 'contextual')}
    contextual = reports['contextual']
    adjacent_misses = [row['id'] for row in contextual['queries'] if not row['top1_correct']
                       and row['retrieved_messages'] and row['expected_message_id'] in
                       row['retrieved_messages'][0]['context_message_ids']]
    comparison = {
        'contextual_vs_lexical': compare_reports(reports['lexical'], contextual),
        'contextual_vs_original_only_semantic': compare_reports(reports['semantic'], contextual),
        'incorrect_top1_with_expected_only_in_context': adjacent_misses,
        'note': 'Neighbor-only matches remain incorrect; no credit or target changes are applied.',
    }
    (ROOT / 'results/contextual_comparison.json').write_bytes(
        (json.dumps(comparison, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(comparison, indent=2))


if __name__ == '__main__':
    main()
