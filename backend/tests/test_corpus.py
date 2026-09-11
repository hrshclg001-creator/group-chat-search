"""Corpus acceptance, determinism and deliberate corruption checks."""

import copy
import hashlib
import random
from collections import Counter
from datetime import datetime

import pytest

from scripts.corpus_config import MESSAGE_TYPES, PARTICIPANTS, SEED, THREAD_IDS
from scripts.generate_data import DEFAULT_OUTPUT, encode_messages, generate_corpus, write_corpus
from scripts.validate_data import validate_corpus, validate_files


@pytest.fixture(scope='module')
def corpus():
    return generate_corpus()


def test_count_and_required_fields(corpus):
    messages, metadata = corpus
    assert len(messages) >= 4200 >= 4000
    assert metadata['message_count'] == len(messages)
    assert all({'id', 'timestamp', 'sender', 'text', 'message_type'} <= row.keys() for row in messages)
    assert len({row['id'] for row in messages}) == len(messages)
    assert messages[0]['id'] == 'MSG_000001'
    assert messages[-1]['id'] == f'MSG_{len(messages):06d}'


def test_exactly_eight_realistic_fictional_participants(corpus):
    messages, metadata = corpus
    assert len(metadata['participants']) == 8
    assert len({person['id'] for person in PARTICIPANTS}) == 8
    assert {row['sender'] for row in messages} == {person['name'] for person in PARTICIPANTS}
    assert all(len(person['name'].split()) >= 2 for person in PARTICIPANTS)
    assert metadata['synthetic'] is True


def test_six_month_calendar_and_fixed_reference_date(corpus):
    messages, metadata = corpus
    stamps = [datetime.fromisoformat(row['timestamp']) for row in messages]
    assert stamps == sorted(stamps)
    assert stamps[0].date().isoformat() == '2026-03-01'
    assert stamps[-1].date().isoformat() == '2026-08-31'
    assert (stamps[-1] - stamps[0]).days == 183
    assert len({stamp.date() for stamp in stamps}) == 184
    assert {stamp.month for stamp in stamps} == {3, 4, 5, 6, 7, 8}
    assert all(row['timestamp'].endswith('+05:30') for row in messages)
    assert metadata['reference_date'] == '2026-09-01'


def test_required_message_varieties(corpus):
    messages, _ = corpus
    assert {row['message_type'] for row in messages} == MESSAGE_TYPES
    texts = {row['text'] for row in messages}
    assert {'haan', 'done', 'ok', '😂'} <= texts
    for marker in ('[Image]', '[PDF]', '[Voice message]', 'Forwarded:', 'https://'):
        assert any(marker in text for text in texts)
    assert any('nhi' in text or 'thnks' in text for text in texts)
    assert any('yaar' in text and any(word in text for word in ['trip', 'sea', 'cute']) for text in texts)


@pytest.mark.parametrize('thread_id,expected,rejected,distractor', [
    ('TRIP_MANALI', ['Manali', 'June 10-15', '8,700'], ['Goa'], 'charger'),
    ('HACKATHON_STACK', ['React', 'Vite', 'FastAPI', 'SQLite'], ['MERN', 'Flutter', 'Firebase', 'Django'], 'badminton'),
    ('BIRTHDAY_EVENT', ['Nukkad Cafe', 'July 25', '2,900', '362.50'], ['rooftop', 'Bowling', 'lawn', 'common room'], 'cat'),
])
def test_long_decisions_have_outcomes_alternatives_and_interruptions(corpus, thread_id, expected, rejected, distractor):
    messages, metadata = corpus
    rows = [row for row in messages if row.get('thread_id') == thread_id]
    assert len(rows) == 72
    assert len({row['timestamp'][:10] for row in rows}) == 6
    assert len({row['sender'] for row in rows}) == 8
    assert (datetime.fromisoformat(rows[-1]['timestamp']) - datetime.fromisoformat(rows[0]['timestamp'])).days >= 14
    conclusion_id = metadata['decision_threads'][thread_id]['conclusion_message_id']
    conclusion = next(row for row in rows if row['id'] == conclusion_id)
    assert all(term in conclusion['text'] for term in expected)
    earlier = '\n'.join(row['text'] for row in rows if row['id'] < conclusion_id)
    assert all(term.lower() in earlier.lower() for term in rejected)
    assert distractor in earlier.lower()
    assert sum(row['id'] > conclusion_id for row in rows) >= 12
    assert any(rows[0]['id'] < row['id'] < rows[-1]['id'] and not row.get('thread_id') for row in messages)


def test_hackathon_final_wording_differs_from_initial_proposal(corpus):
    messages, metadata = corpus
    final_id = metadata['decision_threads']['HACKATHON_STACK']['conclusion_message_id']
    final_text = next(row['text'] for row in messages if row['id'] == final_id)
    assert 'FastAPI' in final_text and 'SQLite' in final_text
    assert 'MERN' not in final_text and 'Express' not in final_text and 'Mongo' not in final_text


def test_validation_and_audit_hash(corpus):
    messages, metadata = corpus
    report = validate_corpus(messages, metadata)
    assert report['participants'] == 8
    assert set(report['thread_counts']) == set(THREAD_IDS)
    assert metadata['sha256'] == hashlib.sha256(encode_messages(messages)).hexdigest()


def test_generation_is_deterministic_and_does_not_change_global_rng(tmp_path):
    state = random.getstate()
    first = tmp_path / 'first'
    second = tmp_path / 'second'
    write_corpus(first)
    write_corpus(second)
    assert random.getstate() == state
    for filename in ('messages.jsonl', 'corpus_metadata.json'):
        assert (first / filename).read_bytes() == (second / filename).read_bytes()
    assert validate_files(first)['message_count'] >= 4200
    assert b'\r\n' not in (first / 'messages.jsonl').read_bytes()


def test_different_seed_changes_background_not_decision_content(corpus):
    messages, _ = corpus
    other, _ = generate_corpus(SEED + 1)
    assert encode_messages(messages) != encode_messages(other)
    for thread_id in THREAD_IDS:
        assert [row['text'] for row in messages if row.get('thread_id') == thread_id] == [
            row['text'] for row in other if row.get('thread_id') == thread_id]


def test_saved_corpus_matches_generator(corpus):
    messages, metadata = corpus
    assert validate_files(DEFAULT_OUTPUT)['message_count'] == len(messages)
    assert (DEFAULT_OUTPUT / 'messages.jsonl').read_bytes() == encode_messages(messages)
    assert metadata['generation']['seed'] == SEED


@pytest.mark.parametrize('mutation,error', [
    ('too_few', 'at least 4200'),
    ('duplicate_id', 'IDs must be unique'),
    ('missing_field', 'Missing required'),
    ('extra_participant', 'eight configured'),
    ('unknown_sender', 'Sender name'),
    ('empty_text', 'nonempty'),
    ('unknown_type', 'Unknown message type'),
    ('out_of_range', 'outside corpus'),
    ('naive_timestamp', 'Timestamps must use'),
    ('wrong_reference', 'Reference date'),
    ('wrong_hash', 'hash mismatch'),
    ('missing_thread', 'missing or too short'),
    ('invalid_conclusion', 'Invalid conclusion'),
])
def test_validator_rejects_corruption(corpus, mutation, error):
    messages, metadata = copy.deepcopy(corpus)
    if mutation == 'too_few':
        messages = messages[:3999]
    elif mutation == 'duplicate_id':
        messages[1]['id'] = messages[0]['id']
    elif mutation == 'missing_field':
        del messages[0]['text']
    elif mutation == 'extra_participant':
        metadata['participants'].append({'id': 'P09', 'name': 'Ninth Person'})
    elif mutation == 'unknown_sender':
        messages[0]['sender'] = 'Ninth Person'
    elif mutation == 'empty_text':
        messages[0]['text'] = ' '
    elif mutation == 'unknown_type':
        messages[0]['message_type'] = 'unknown'
    elif mutation == 'out_of_range':
        messages[-1]['timestamp'] = '2026-09-01T23:50:00+05:30'
    elif mutation == 'naive_timestamp':
        messages[0]['timestamp'] = '2026-03-01T07:05:00'
    elif mutation == 'wrong_reference':
        metadata['reference_date'] = '2026-09-02'
    elif mutation == 'wrong_hash':
        metadata['sha256'] = '0' * 64
    elif mutation == 'missing_thread':
        for row in messages:
            if row.get('thread_id') == 'TRIP_MANALI':
                del row['thread_id']
        metadata['sha256'] = hashlib.sha256(encode_messages(messages)).hexdigest()
    elif mutation == 'invalid_conclusion':
        metadata['decision_threads']['TRIP_MANALI']['conclusion_message_id'] = messages[0]['id']
    with pytest.raises(ValueError, match=error):
        validate_corpus(messages, metadata)


def test_validator_rejects_missing_media_variety(corpus):
    messages, metadata = copy.deepcopy(corpus)
    for row in messages:
        if row['message_type'] == 'voice':
            row['text'] = 'Audio removed from this intentionally corrupted test copy'
            row['message_type'] = 'text'
    metadata['sha256'] = hashlib.sha256(encode_messages(messages)).hexdigest()
    metadata['message_type_counts'] = dict(Counter(row['message_type'] for row in messages))
    with pytest.raises(ValueError, match='Missing required message varieties'):
        validate_corpus(messages, metadata)


def test_validator_detects_tampered_file(tmp_path):
    write_corpus(tmp_path)
    with (tmp_path / 'messages.jsonl').open('ab') as stream:
        stream.write(b'\n')
    # Hash check comes before parsing so even whitespace tampering is reported.
    with pytest.raises(ValueError, match='hash mismatch'):
        validate_files(tmp_path)
