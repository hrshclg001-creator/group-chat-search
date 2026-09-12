"""Independent fixtures verify reporting without changing frozen labels."""

import copy
import csv
import json

import pytest

from backend.app.search.corpus import Message
from evaluation import evaluate
from evaluation.metrics import summarize
from evaluation.reporting import (
    METHODS, comparison_records, failure_lines, make_chart, terminal_table, write_comparison_artifacts,
)


def measured_fixtures(hard_count=10):
    reports = {}
    messages = {f'M{i}': Message(f'M{i}', 'Test Student', '2026-08-01T10:00:00+05:30', f'expected original {i}')
                for i in range(40)}
    for method, divisor in zip(METHODS, (4, 3, 5, 2)):
        rows = []
        for i in range(40):
            expected = f'M{i}'
            retrieved = expected if i % divisor == 0 else 'other'
            rows.append({
                'id': f'query-{i}', 'query': f'fixture question {i}', 'expected_message_id': expected,
                'category': 'semantic' if i < 20 else 'person' if i < 30 else 'time',
                'zero_word_overlap': i < hard_count, 'retrieved_ids': [retrieved],
                'top1_correct': retrieved == expected,
                'retrieved_messages': [{'id': retrieved, 'sender': 'Test Student',
                    'timestamp': '2026-08-01T10:00:00+05:30', 'text': 'retrieved original',
                    'hybrid_score': .4, 'semantic_score': .5, 'contextual_score': .3, 'lexical_score': .2}],
            })
        reports[method] = {'method': method, 'queries': rows, 'metrics': summarize(rows),
                           'input_sha256': {'fixture': 'identical'}, 'query_count': 40,
                           'corpus_message_count': 4200, 'reference_date': '2026-09-01'}
    return reports, messages


@pytest.mark.parametrize('hard_count', [8, 10, 12])
def test_terminal_table_labels_real_subset_and_retains_numerators(hard_count):
    reports, _ = measured_fixtures(hard_count)
    table = terminal_table(reports)
    assert f'Hard-{hard_count}' in table
    assert '25.0% (10/40)' in table
    assert 'Gap (pp)' in table
    for method in METHODS:
        assert method.capitalize() in table
    if hard_count != 8:
        assert 'Hard-8' not in table


def test_diagnostics_include_expected_and_retrieved_originals_and_all_scores():
    reports, messages = measured_fixtures()
    report = reports['hybrid']
    lines = '\n'.join(failure_lines(report, messages))
    assert 'INCORRECT query-1' in lines and 'INCORRECT query-0 ' not in lines
    assert 'Expected M1 |' in lines and 'expected original 1' in lines
    assert 'Retrieved other (rank 1)' in lines and 'retrieved original' in lines
    assert 'hybrid_score=0.400000' in lines and 'lexical_score=0.200000' in lines
    report['queries'][1]['retrieved_messages'] = []
    report['queries'][1]['retrieved_ids'] = []
    assert 'no eligible result' in '\n'.join(failure_lines(report, messages))


def test_artifacts_agree_with_rankings_and_csv_is_numeric(tmp_path):
    reports, messages = measured_fixtures(12)
    comparison = write_comparison_artifacts(reports, messages, tmp_path)
    with (tmp_path / 'comparison.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert [row['method'] for row in rows] == list(METHODS)
    assert all(int(row['hard_top1_total']) == 12 for row in rows)
    assert float(rows[3]['top1_percent']) == reports['hybrid']['metrics']['top1_accuracy']['percent']
    assert int(rows[3]['person_top1_total']) == 10
    summary = (tmp_path / 'evaluation_summary.md').read_text(encoding='utf-8')
    assert 'Hard-12' in summary and 'development-set' in summary
    assert '50.0% (20/40)' in summary
    assert (tmp_path / 'benchmark.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    assert json.loads((tmp_path / 'hybrid.json').read_text(encoding='utf-8')) == reports['hybrid']
    assert comparison['metrics_by_method']['lexical'] == summarize(reports['lexical']['queries'])


def test_chart_bars_use_measured_rates_and_full_percent_axis():
    reports, _ = measured_fixtures(10)
    figure = make_chart(reports)
    axes = figure.axes[0]
    records = comparison_records(reports)
    expected = [row['top1_percent'] for row in records] + [row['hard_top1_percent'] for row in records]
    assert [bar.get_height() for bar in axes.patches] == expected
    assert axes.get_ylim() == (0, 100)
    assert any('Hard-10' in text.get_text() for text in axes.get_legend().get_texts())
    figure.clear()


def test_inconsistent_report_is_rejected_before_writing(tmp_path):
    reports, messages = measured_fixtures()
    reports['hybrid']['metrics']['top1_accuracy']['percent'] = 99
    with pytest.raises(ValueError, match='disagree'):
        write_comparison_artifacts(reports, messages, tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_all_runs_four_methods_with_shared_encoder_and_no_label_changes(monkeypatch, tmp_path):
    reports, messages = measured_fixtures()
    original = copy.deepcopy(reports)
    calls = []
    saved = []
    encoder = object()
    monkeypatch.setattr(evaluate, 'validate_files', lambda: {})
    from backend.app.search import embedding
    monkeypatch.setattr(embedding, 'LocalEncoder', lambda: encoder)

    def run(method, encoder=None):
        calls.append((method, encoder))
        return reports[method], messages

    monkeypatch.setattr(evaluate, 'run_method', run)
    monkeypatch.setattr(evaluate, 'write_comparison_artifacts', lambda *args: saved.append(args))
    assert evaluate.run_all(tmp_path) == reports
    assert [method for method, _ in calls] == list(METHODS)
    assert calls[0][1] is None and all(value is encoder for _, value in calls[1:])
    assert len(saved) == 1 and reports == original


def test_partial_run_does_not_overwrite_existing_artifacts(monkeypatch, tmp_path):
    reports, messages = measured_fixtures()
    prior = tmp_path / 'lexical.json'
    prior.write_text('previous measured run', encoding='utf-8')
    monkeypatch.setattr(evaluate, 'validate_files', lambda: {})
    from backend.app.search import embedding
    monkeypatch.setattr(embedding, 'LocalEncoder', lambda: object())

    def fail_after_lexical(method, encoder=None):
        if method != 'lexical':
            raise FileNotFoundError('model missing')
        return reports[method], messages

    monkeypatch.setattr(evaluate, 'run_method', fail_after_lexical)
    with pytest.raises(FileNotFoundError, match='model missing'):
        evaluate.run_all(tmp_path)
    assert prior.read_text(encoding='utf-8') == 'previous measured run'


def test_cli_all_and_single_method_are_mutually_exclusive(monkeypatch):
    monkeypatch.setattr('sys.argv', ['evaluate.py', '--all', '--method', 'lexical'])
    with pytest.raises(SystemExit) as failure:
        evaluate.main()
    assert failure.value.code == 2
