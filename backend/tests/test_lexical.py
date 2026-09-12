"""Small independent fixtures test retrieval behavior without evaluation labels."""

import json

import pytest

from app.search import LexicalSearch, Message, load_corpus


def message(number, text, sender='Test Student'):
    return Message(f'MSG_{number:06d}', sender, '2026-03-01T10:00:00+05:30', text)


@pytest.fixture
def messages():
    return [message(1, 'Fresh sandwiches at the canteen'),
            message(2, 'Database transactions and indexing practice'),
            message(3, 'Badminton doubles tournament tonight')]


def test_exact_match_preserves_original_fields_and_orders_scores(messages):
    searcher = LexicalSearch(messages)
    hit = searcher.search(messages[1].text, top_k=1)[0]
    assert hit.to_dict() == {**messages[1].__dict__, 'lexical_score': pytest.approx(1.0)}
    hits = searcher.search('canteen practice tournament', top_k=3)
    assert len(hits) == 3
    assert [hit.lexical_score for hit in hits] == sorted((hit.lexical_score for hit in hits), reverse=True)
    assert all(0 < hit.lexical_score <= 1.00000001 for hit in hits)


def test_character_channel_recovers_a_typo_without_a_word_match(messages):
    searcher = LexicalSearch(messages)
    query = 'sandwches'
    assert searcher.word_vectorizer.transform([query]).nnz == 0
    hits = searcher.search(query, top_k=1)
    assert hits[0].id == messages[0].id
    assert 0 < hits[0].lexical_score <= searcher.CHARACTER_WEIGHT


def test_word_channel_contains_unigrams_and_bigrams(messages):
    searcher = LexicalSearch(messages)
    vocabulary = searcher.word_vectorizer.vocabulary_
    assert 'database' in vocabulary
    assert 'database transactions' in vocabulary
    assert searcher.search('DATABASE TRANSACTIONS', top_k=1)[0].id == messages[1].id


def test_ties_are_stable_by_id_independent_of_input_order():
    rows = [message(3, 'identical text'), message(1, 'identical text'), message(2, 'identical text')]
    first = LexicalSearch(rows).search('identical text', top_k=99)
    second = LexicalSearch(reversed(rows)).search('identical text', top_k=99)
    assert [hit.id for hit in first] == ['MSG_000001', 'MSG_000002', 'MSG_000003']
    assert first == second


def test_empty_and_unseen_queries_return_no_arbitrary_zero_score_hits(messages):
    searcher = LexicalSearch(messages)
    assert searcher.search(' \n ') == []
    assert searcher.search('zzzzzzzzzzzz') == []


@pytest.mark.parametrize('top_k', [0, -1, True, 1.5, '3'])
def test_invalid_top_k_is_rejected(messages, top_k):
    with pytest.raises(ValueError, match='positive integer'):
        LexicalSearch(messages).search('canteen', top_k=top_k)


def test_nontext_query_and_invalid_corpus_are_rejected(messages):
    with pytest.raises(TypeError, match='string'):
        LexicalSearch(messages).search(None)
    with pytest.raises(ValueError, match='empty'):
        LexicalSearch([])
    with pytest.raises(ValueError, match='Duplicate'):
        LexicalSearch([messages[0], messages[0]])
    with pytest.raises(ValueError, match='nonempty'):
        LexicalSearch([message(1, ' ')])


def test_emoji_only_corpus_does_not_crash_on_empty_word_vocabulary():
    searcher = LexicalSearch([message(1, '😂'), message(2, '🎂')])
    assert searcher.word_matrix is None
    assert searcher.search('😂')[0].id == 'MSG_000001'


def test_sender_timestamp_ids_and_extra_annotations_are_not_indexed(tmp_path):
    path = tmp_path / 'messages.jsonl'
    record = {**message(1, 'apples oranges', sender='Zyxwvu').__dict__,
              'metadata': {'topic': 'xylophone'}, 'notes': 'quizzical', 'thread_id': 'NEBULA'}
    path.write_text(json.dumps(record) + '\n', encoding='utf-8')
    searcher = LexicalSearch.from_jsonl(path)
    for query in ('Zyxwvu', '2026', 'MSG_000001', 'xylophone', 'quizzical', 'NEBULA'):
        assert searcher.search(query) == []
    assert searcher.search('apples')[0].sender == 'Zyxwvu'


@pytest.mark.parametrize('kind,error', [
    ('empty', 'empty'), ('invalid_json', 'line 1'), ('missing_field', 'line 1'),
    ('duplicate', 'duplicate message ID'), ('naive_time', 'timezone-aware'),
])
def test_loader_rejects_malformed_inputs(tmp_path, kind, error):
    path = tmp_path / 'bad.jsonl'
    row = message(1, 'valid text').__dict__.copy()
    if kind == 'empty':
        text = ''
    elif kind == 'invalid_json':
        text = '{broken\n'
    elif kind == 'duplicate':
        text = (json.dumps(row) + '\n') * 2
    else:
        if kind == 'missing_field':
            del row['sender']
        else:
            row['timestamp'] = '2026-03-01T10:00:00'
        text = json.dumps(row) + '\n'
    path.write_text(text, encoding='utf-8')
    with pytest.raises(ValueError, match=error):
        load_corpus(path)


def test_real_corpus_loads_only_original_fields():
    rows = load_corpus()
    assert len(rows) == 4634
    assert rows[0].id == 'MSG_000001'
    assert rows[-1].id == 'MSG_004634'
    assert set(rows[0].__dict__) == {'id', 'sender', 'timestamp', 'text'}
