"""Tables, diagnostics and plots derived solely from validated measured runs."""

import csv
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import platform

from .compare import compare_all
from .validate_queries import sha256


METHODS = ('lexical', 'semantic', 'contextual', 'hybrid')
CATEGORIES = ('person', 'time', 'semantic')
SCORE_FIELDS = ('hybrid_score', 'semantic_score', 'contextual_score', 'lexical_score', 'reranker_score', 'metadata_bonus')


def display_rate(rate):
    if rate['percent'] is None:
        return f"n/a ({rate['correct']}/{rate['total']})"
    return f"{rate['percent']:.1f}% ({rate['correct']}/{rate['total']})"


def table_data(reports):
    compare_all(reports)  # Reject mixed inputs and aggregates that disagree with ranks.
    hard_counts = {report['metrics']['zero_word_overlap_top1_accuracy']['total'] for report in reports.values()}
    if len(hard_counts) != 1:
        raise ValueError('Hard-subset counts differ between methods')
    headers = ['Method', 'Top-1', 'Recall@3', f'Hard-{hard_counts.pop()}', 'Person', 'Time', 'Semantic', 'Gap (pp)']
    rows = []
    for method in METHODS:
        metrics = reports[method]['metrics']
        gap = metrics['overall_minus_hard_percentage_points']
        rows.append([method.capitalize(),
                     *(display_rate(metrics[key]) for key in ('top1_accuracy', 'recall_at_3', 'zero_word_overlap_top1_accuracy')),
                     *(display_rate(metrics['top1_accuracy_by_category'][category]) for category in CATEGORIES),
                     'n/a' if gap is None else f'{gap:+.1f}'])
    return headers, rows


def terminal_table(reports):
    headers, rows = table_data(reports)
    widths = [max(len(row[i]) for row in [headers, *rows]) for i in range(len(headers))]
    lines = ['  '.join(value.ljust(width) for value, width in zip(row, widths)) for row in [headers, *rows]]
    lines.insert(1, '  '.join('-' * width for width in widths))
    return '\n'.join(lines)


def failure_lines(report, messages):
    """Include expected original text and every top-three candidate's scores."""
    lines = []
    for row in report['queries']:
        if row['retrieved_ids'] and row['retrieved_ids'][0] == row['expected_message_id']:
            continue
        expected = messages[row['expected_message_id']]
        lines.extend([
            f"\nINCORRECT {row['id']} [{row['category']}] {row['query']}",
            f'  Expected {expected.id} | {expected.sender} | {expected.timestamp} | {expected.text}',
        ])
        if not row['retrieved_messages']:
            lines.append('  Retrieved: no eligible result')
        for rank, hit in enumerate(row['retrieved_messages'], 1):
            scores = ', '.join(f'{field}={hit[field]:.6f}' for field in SCORE_FIELDS if isinstance(hit.get(field), (int, float)))
            lines.append(f"  Retrieved {hit['id']} (rank {rank}) | {scores or 'scores unavailable'} | "
                         f"{hit['sender']} | {hit['timestamp']} | {hit['text']}")
        lines.append(f"  Top 3: {', '.join(row['retrieved_ids']) or '(empty)'}")
    return lines


def comparison_records(reports):
    table_data(reports)
    records = []
    for method in METHODS:
        metrics = reports[method]['metrics']
        record = {'method': method}
        groups = [('top1', metrics['top1_accuracy']), ('recall_at_3', metrics['recall_at_3']),
                  ('hard_top1', metrics['zero_word_overlap_top1_accuracy'])]
        groups += [(f'{category}_top1', metrics['top1_accuracy_by_category'][category]) for category in CATEGORIES]
        for name, rate in groups:
            for field in ('correct', 'total', 'percent'):
                record[f'{name}_{field}'] = rate[field]
        record['overall_minus_hard_percentage_points'] = metrics['overall_minus_hard_percentage_points']
        records.append(record)
    return records


def make_chart(reports):
    """Use a noninteractive canvas; no desktop session or GUI backend needed."""
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    records = comparison_records(reports)
    hard_count = records[0]['hard_top1_total']
    overall_count = records[0]['top1_total']
    if hard_count == 0:
        raise ValueError('A hard-subset chart requires at least one hard query')
    figure = Figure(figsize=(10.5, 5.8), facecolor='#fafbf8')
    FigureCanvasAgg(figure)
    axes = figure.add_subplot(111)
    axes.set_facecolor('#fafbf8')
    width = .34
    for shift, prefix, label, color in (
        (-width / 2, 'top1', f'Overall Top-1 (n={overall_count})', '#286348'),
        (width / 2, 'hard_top1', f'Hard-{hard_count} Top-1 (zero-word-overlap)', '#cf9852'),
    ):
        bars = axes.bar([i + shift for i in range(len(records))], [row[f'{prefix}_percent'] for row in records],
                        width, label=label, color=color, zorder=3)
        for bar, row in zip(bars, records):
            height = bar.get_height()
            axes.annotate(f"{height:.1f}%\n({row[f'{prefix}_correct']}/{row[f'{prefix}_total']})",
                          (bar.get_x() + bar.get_width() / 2, height), xytext=(0, 5),
                          textcoords='offset points', ha='center', va='bottom', fontsize=9, color='#26352b')
    axes.set_xticks(range(len(records)), [row['method'].capitalize() for row in records])
    axes.set_ylim(0, 100)
    axes.set_ylabel('Top-1 accuracy (%)')
    axes.set_title('Group-chat retrieval: overall and hard-query accuracy', loc='left', pad=18, fontsize=14)
    axes.grid(axis='y', alpha=.20, zorder=0)
    axes.spines[['top', 'right']].set_visible(False)
    axes.legend(loc='upper left', frameon=False, fontsize=9)
    figure.text(.09, .035, 'Same frozen corpus and labels. Hybrid weights were selected on this query set; no held-out accuracy is claimed.', fontsize=8, color='#53614f')
    figure.subplots_adjust(left=.09, right=.98, top=.88, bottom=.14)
    return figure


def summary_text(reports, generated_at):
    headers, rows = table_data(reports)
    first = reports[METHODS[0]]
    best = max(METHODS, key=lambda method: reports[method]['metrics']['top1_accuracy']['percent'])
    hard_count = first['metrics']['zero_word_overlap_top1_accuracy']['total']
    lines = ['# Retrieval evaluation', '', f'Automatically generated at {generated_at}.', '',
             f"All four methods were run on the same frozen {first['query_count']} queries and "
             f"{first['corpus_message_count']:,} synthetic messages. Reference date: {first['reference_date']}. "
             f'**Hard-{hard_count}** means the complete zero-meaningful-word-overlap subset; it is not restricted to eight queries.', '',
             '| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    lines += ['| ' + ' | '.join(row) + ' |' for row in rows]
    lines += ['', 'Every accuracy cell includes correct/total. Gap is overall Top-1 minus hard Top-1, in signed percentage points. '
              'Only the exact matching message ID receives credit; neighboring answers do not.', '',
              f"Highest measured overall Top-1: **{best.capitalize()}**, {display_rate(reports[best]['metrics']['top1_accuracy'])}.", '']
    counts = ', '.join(f"{method} {report['metrics']['top1_accuracy']['total'] - report['metrics']['top1_accuracy']['correct']}"
                       for method, report in ((method, reports[method]) for method in METHODS))
    lines += [f'Top-1 failures by method: {counts}. Expected original messages, all top-three retrieved messages and available score components are in [failed_queries.txt](failed_queries.txt).', '',
              '**Limitations:** Hybrid weights were selected on this same query set, so these are development-set results, not held-out generalization accuracy. '
              'Zero-overlap questions can remain difficult even when person/time retrieval improves. No labels or ranking settings were changed by this run.', '',
              'Reproduce from the repository root after installing the locked backend dependencies and preparing the local model:', '',
              '```text', 'python evaluation/evaluate.py --all', '```', '',
              'Artifacts: [CSV](comparison.csv), [comparison JSON](comparison.json), [chart](benchmark.png), '
              '[lexical](lexical.json), [semantic](semantic.json), [contextual](contextual.json), [hybrid](hybrid.json). '
              'Per-method JSON records model/dependency versions, configuration, source/input hashes and rankings. '
              'Comparison JSON records reporting versions and artifact hashes.', '']
    return '\n'.join(lines)


def write_comparison_artifacts(reports, messages, directory):
    """Write reports only after every method has finished and inputs agree."""
    directory = Path(directory)
    comparison = compare_all(reports)
    records = comparison_records(reports)
    generated_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    # Render before touching existing outputs so a missing matplotlib cannot
    # leave refreshed JSON beside an old chart from another run.
    figure = make_chart(reports)
    directory.mkdir(parents=True, exist_ok=True)
    for method in METHODS:
        path = directory / f'{method}.json'
        path.write_bytes((json.dumps(reports[method], ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8'))
    with (directory / 'comparison.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(records)
    figure.savefig(directory / 'benchmark.png', dpi=180)
    figure.clear()
    summary = summary_text(reports, generated_at)
    (directory / 'evaluation_summary.md').write_bytes(summary.encode('utf-8'))
    failures = []
    for method in METHODS:
        failures.append(f'\n=== {method.upper()} FAILED QUERIES ===')
        failures.extend(failure_lines(reports[method], messages))
    (directory / 'failed_queries.txt').write_bytes(('\n'.join(failures) + '\n').encode('utf-8'))
    comparison['generated_at_utc'] = generated_at
    comparison['report_sha256'] = {f'results/{method}.json': sha256(directory / f'{method}.json') for method in METHODS}
    comparison['artifact_sha256'] = {f'results/{name}': sha256(directory / name)
                                     for name in ('comparison.csv', 'benchmark.png', 'evaluation_summary.md', 'failed_queries.txt')}
    comparison['reporting_environment'] = {
        'python': platform.python_version(), 'matplotlib': version('matplotlib'), 'numpy': version('numpy'),
    }
    (directory / 'comparison.json').write_bytes((json.dumps(comparison, indent=2, allow_nan=False) + '\n').encode('utf-8'))
    return comparison
