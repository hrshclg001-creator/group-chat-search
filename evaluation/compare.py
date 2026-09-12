"""Compare measured runs only when they use identical frozen inputs."""

import argparse
import json
from pathlib import Path

from .metrics import summarize
from .validate_queries import sha256

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


def compare_all(reports):
    required = ('lexical', 'semantic', 'contextual', 'hybrid')
    if set(reports) != set(required):
        raise ValueError('Four reports required: lexical, semantic, contextual, hybrid')
    for name, report in reports.items():
        if report['method'] != name:
            raise ValueError('Report method does not match its file')
    return {
        'input_sha256': reports['hybrid']['input_sha256'],
        'metrics_by_method': {method: reports[method]['metrics'] for method in required},
        'hybrid_vs_baselines': {method: compare_reports(reports[method], reports['hybrid'])
                                for method in required[:-1]},
        'limitations': 'Hybrid weights were selected on these same frozen queries; baseline configurations were untuned. No held-out accuracy is claimed.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true', help='Compare all four methods, including hybrid')
    args = parser.parse_args()
    if args.all:
        from .validate_queries import validate_files
        validate_files()
        paths = {method: ROOT / f'results/{method}.json' for method in ('lexical', 'semantic', 'contextual', 'hybrid')}
        reports = {method: json.loads(path.read_text(encoding='utf-8')) for method, path in paths.items()}
        comparison = compare_all(reports)
        for path, digest in comparison['input_sha256'].items():
            if sha256(ROOT / path) != digest:
                raise ValueError('Report input hash differs from the frozen files on disk')
        comparison['report_sha256'] = {str(path.relative_to(ROOT)).replace('\\', '/'): sha256(path) for path in paths.values()}
        destination = ROOT / 'results/comparison.json'
        destination.write_bytes((json.dumps(comparison, indent=2) + '\n').encode('utf-8'))
        print(json.dumps(comparison['metrics_by_method'], indent=2))
        print(f'Saved {destination}')
        return
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
