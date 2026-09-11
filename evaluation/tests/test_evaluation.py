"""Meaningful contract, overlap and freeze-integrity checks for the label set."""

import copy
import json
import shutil

import pytest

from evaluation.overlap import CONVENTION, STOPWORDS, content_words, overlap_details
from evaluation.validate_queries import (
    CORPUS_PATH, FROZEN_PATHS, MANIFEST_PATH, QUERY_PATH, ROOT,
    validate_files, validate_freeze, validate_queries,
)


@pytest.fixture(scope='module')
def dataset():
    return (json.loads(QUERY_PATH.read_text(encoding='utf-8')),
            [json.loads(line) for line in CORPUS_PATH.read_text(encoding='utf-8').splitlines()])


def test_frozen_dataset_counts_targets_and_all_threads():
    report = validate_files()
    assert report['freeze_verified'] is True
    assert report['query_count'] == 40
    assert report['category_counts'] == {'semantic': 20, 'person': 10, 'time': 10}
    assert report['hard_query_count'] == 10
    assert report['distinct_target_count'] == 37
    assert report['decision_thread_ids_covered'] == ['BIRTHDAY_EVENT', 'HACKATHON_STACK', 'TRIP_MANALI']


def test_all_flags_agree_with_computed_overlap(dataset):
    queries, messages = dataset
    targets = {message['id']: message for message in messages}
    for item in queries:
        details = overlap_details(item['query'], targets[item['expected_message_id']]['text'])
        assert details['query_content_words'] and details['target_content_words']
        assert details['zero_word_overlap'] is item['zero_word_overlap']


def test_normalization_keeps_numbers_names_time_words_and_negation():
    assert content_words("ＡＡＲＡＶ’S [PDF] can't cost 700! 😂") == {'aarav', 'pdf', 'not', 'cost', '700'}
    assert {'no', 'not', 'nahi', 'mat', 'may', 'last', 'month', 'yesterday', 'manali', 'sqlite'} <= content_words(
        'no not nahi mat May last month yesterday Manali SQLite')
    assert content_words('hai hain ka ki ke ko mein aur kya') == set()
    assert len(STOPWORDS) == len(CONVENTION['stopwords'])


def test_no_stemming_or_translation_and_no_empty_hard_examples():
    assert content_words('rooms room') == {'rooms', 'room'}
    assert content_words('baarish rain') == {'baarish', 'rain'}
    assert overlap_details('What is it? 😂', 'the and') ['zero_word_overlap'] is False
    assert overlap_details('Emergency buffer?', 'buffer for unexpected expenses')['zero_word_overlap'] is False


@pytest.mark.parametrize('mutation,expected_error', [
    ('count', 'exactly 40'), ('missing_field', 'required fields'),
    ('duplicate_id', 'unique and ordered'), ('unknown_target', 'target ID does not exist'),
    ('bad_category', 'Unknown query category'), ('missing_category', 'All three'),
    ('string_flag', 'JSON boolean'), ('too_few_hard', 'at least 8'),
    ('incorrect_flag', 'flag mismatch'), ('empty_notes', 'notes must be nonempty'),
    ('empty_content', 'meaningful content'), ('duplicate_query', 'Duplicate query text'),
])
def test_rejects_bad_labels_without_mutating_them(dataset, mutation, expected_error):
    queries, messages = copy.deepcopy(dataset)
    if mutation == 'count':
        queries.pop()
    elif mutation == 'missing_field':
        del queries[0]['notes']
    elif mutation == 'duplicate_id':
        queries[1]['id'] = queries[0]['id']
    elif mutation == 'unknown_target':
        queries[0]['expected_message_id'] = 'MSG_999999'
    elif mutation == 'bad_category':
        queries[0]['category'] = 'other'
    elif mutation == 'missing_category':
        for query in queries:
            query['category'] = 'semantic'
    elif mutation == 'string_flag':
        queries[0]['zero_word_overlap'] = 'true'
    elif mutation == 'too_few_hard':
        for query in queries:
            query['zero_word_overlap'] = False
    elif mutation == 'incorrect_flag':
        queries[0]['zero_word_overlap'] = False
    elif mutation == 'empty_notes':
        queries[0]['notes'] = ' '
    elif mutation == 'empty_content':
        queries[0]['query'] = 'What is it?'
    elif mutation == 'duplicate_query':
        queries[1]['query'] = queries[0]['query']
    before = copy.deepcopy(queries)
    with pytest.raises(ValueError, match=expected_error):
        validate_queries(queries, messages)
    assert queries == before


@pytest.mark.parametrize('relative_path', [
    'evaluation/queries.json', 'backend/data/messages.jsonl',
    'evaluation/overlap_convention.json',
])
def test_freeze_detects_changes_to_labels_corpus_and_convention(tmp_path, dataset, relative_path):
    for path in FROZEN_PATHS:
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, destination)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    report = validate_queries(*dataset)
    validate_freeze(manifest, report, root=tmp_path)
    with (tmp_path / relative_path).open('ab') as stream:
        stream.write(b'\n')
    with pytest.raises(ValueError, match='Frozen hash mismatch'):
        validate_freeze(manifest, report, root=tmp_path)


def test_freeze_inventory_cannot_silently_omit_labels(dataset):
    manifest = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    del manifest['sha256']['evaluation/queries.json']
    with pytest.raises(ValueError, match='inventory mismatch'):
        validate_freeze(manifest, validate_queries(*dataset))
