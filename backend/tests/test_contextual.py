"""Offline tests for bounded context, short replies and message identity."""

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from app.search.context import build_contexts, fit_context_to_budget
from app.search.corpus import Message, load_corpus
from app.search.embedding import cached_embeddings
from app.search.semantic import SemanticSearch


def message(index, text=None, minute=None):
    stamp = datetime(2026, 3, 1, 10, tzinfo=timezone.utc) + timedelta(minutes=index if minute is None else minute)
    return Message(f'MSG_{index:06d}', 'Student', stamp.isoformat(), text or f'original message {index}')


class TestTokenizer:
    __test__ = False

    def encode(self, text, add_special_tokens=False):
        return text.split()

    def decode(self, ids, skip_special_tokens=True):
        return ' '.join(ids)

    def num_special_tokens_to_add(self, pair=False):
        return 2


class TestEncoder:
    __test__ = False
    tokenizer = TestTokenizer()
    max_sequence_length = 64
    settings = {'test_model': 'deterministic-fixture-v1'}

    def __init__(self, short_reply='done'):
        self.short_reply = short_reply
        self.calls = []

    def encode(self, texts):
        self.calls.append(list(texts))
        # This controlled fixture makes the anchor score distinguishable; it
        # tests plumbing, not multilingual model quality or benchmark answers.
        return np.array([[1., 0.] if text == 'venue decision' or
                          f'Current message: {self.short_reply}\n' in text else [0., 1.]
                         for text in texts], dtype=np.float32)


def test_window_has_at_most_two_neighbors_each_side_and_preserves_order():
    rows = [message(i) for i in range(1, 8)]
    contexts = build_contexts(reversed(rows))
    assert contexts[0].context_message_ids == ('MSG_000001', 'MSG_000002', 'MSG_000003')
    assert contexts[3].context_message_ids == tuple(row.id for row in rows[1:6])
    assert contexts[-1].context_message_ids == ('MSG_000005', 'MSG_000006', 'MSG_000007')
    for record in contexts:
        assert record.original_text == record.current.text
        assert len(record.messages) <= 5
        assert f'Current message: {record.current.text}' in record.context_text
    with pytest.raises(ValueError, match='two messages'):
        build_contexts(rows, window_size=3)


def test_time_gap_and_equal_timestamp_ties():
    rows = [message(3, minute=100), message(2, minute=1), message(1, minute=1)]
    contexts = build_contexts(rows)
    assert contexts[0].context_message_ids == ('MSG_000001', 'MSG_000002')
    assert contexts[-1].context_message_ids == ('MSG_000003',)


@pytest.mark.parametrize('reply', ['done', 'haan pakka', 'this one', 'ok final'])
def test_short_replies_remain_original_targets_after_contextual_matching(reply):
    rows = [message(1, 'venue options: cafe or lawn'), message(2, reply), message(3, 'booking tomorrow')]
    encoder = TestEncoder(reply)
    searcher = SemanticSearch(rows, contextual=True, encoder=encoder, cache_dir=None)
    hit = searcher.search('venue decision', top_k=1)[0]
    assert hit.id == 'MSG_000002'
    assert hit.text == hit.original_text == reply
    assert 'venue options' in hit.context_text
    assert hit.context_message_ids == ('MSG_000001', 'MSG_000002', 'MSG_000003')
    assert [row['id'] for row in hit.context_messages if row['is_current']] == [hit.id]
    assert rows[1].text == reply


def test_token_budget_trims_neighbors_before_current_and_records_it():
    current_text = 'this is the entire original current message'
    rows = [message(1, 'before ' * 100), message(2, current_text), message(3, 'after ' * 100)]
    record = build_contexts(rows)[1]
    embedding_text, truncated = fit_context_to_budget(record, TestTokenizer(), 32)
    assert len(embedding_text.split()) + 2 <= 32
    assert current_text in embedding_text
    assert record.original_text == current_text
    assert record.context_text.count('before') == 100
    assert 'MSG_000002' not in truncated
    assert set(truncated) == {'MSG_000001', 'MSG_000003'}


def test_oversized_current_message_is_preserved_even_if_embedding_is_truncated():
    text = 'unusually long current message ' * 100
    record = build_contexts([message(1, text)])[0]
    embedding_text, truncated = fit_context_to_budget(record, TestTokenizer(), 32)
    assert len(embedding_text.split()) + 2 <= 32
    assert truncated == ['MSG_000001']
    assert record.original_text == text


def test_original_only_control_uses_no_context():
    rows = [message(1), message(2)]
    encoder = TestEncoder()
    searcher = SemanticSearch(rows, contextual=False, encoder=encoder, cache_dir=None)
    assert encoder.calls[0] == [row.text for row in rows]
    assert all(len(record.context_message_ids) == 1 for record in searcher.contexts)
    assert searcher.search(' ') == []
    with pytest.raises(ValueError, match='positive integer'):
        searcher.search('hello', top_k=0)


def test_cache_reuses_exact_bytes_and_invalidates_text_and_model_changes(tmp_path):
    encoder = TestEncoder()
    matrix, key = cached_embeddings(encoder, ['alpha'], tmp_path)
    repeated, repeated_key = cached_embeddings(encoder, ['alpha'], tmp_path)
    assert len(encoder.calls) == 1
    assert matrix.tobytes() == repeated.tobytes()
    assert key == repeated_key
    _, changed = cached_embeddings(encoder, ['beta'], tmp_path)
    assert changed != key
    encoder.settings = {'test_model': 'new-revision'}
    _, new_model = cached_embeddings(encoder, ['alpha'], tmp_path)
    assert new_model != key


def test_cached_embedding_corruption_is_rejected(tmp_path):
    encoder = TestEncoder()
    _, key = cached_embeddings(encoder, ['alpha'], tmp_path)
    np.savez_compressed(tmp_path / f'{key}.npz', embeddings=np.array([[np.nan, 0]]), matrix_sha256='wrong')
    with pytest.raises(ValueError, match='integrity'):
        cached_embeddings(encoder, ['alpha'], tmp_path)


def test_every_real_message_has_exactly_one_original_context_anchor():
    messages = load_corpus()
    contexts = build_contexts(messages)
    assert len(contexts) == len(messages) == 4634
    assert {record.current.id for record in contexts} == {row.id for row in messages}
    assert all(record.current.text == record.original_text and len(record.messages) <= 5 for record in contexts)
