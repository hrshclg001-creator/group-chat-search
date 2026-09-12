"""Pairwise reranking must preserve constraints, identity and score provenance."""

from dataclasses import replace

import numpy as np
import pytest

from app.query_understanding import QueryParser
from app.search.corpus import Message
from app.search.reranked import RerankedSearch, verify_manifest
from test_hybrid import FixtureEncoder


class PairScorer:
    settings = {'model': 'independent-fixture'}

    def __init__(self):
        self.calls = []

    def score(self, query, messages):
        self.calls.append((query, messages))
        return [.9 if row.text == 'The room is reserved.' else .1 for row in messages]


@pytest.fixture
def engine():
    parser = QueryParser({'reference_date': '2026-09-01', 'timezone': 'Asia/Kolkata',
                          'participants': [{'name': 'Priya Shah'}, {'name': 'Aman Das'}]})
    messages = [Message('C', 'Priya Shah', '2026-08-04T10:00:00+05:30', 'Should we reserve the room?'),
                Message('B', 'Priya Shah', '2026-08-04T10:01:00+05:30', 'The room is reserved.'),
                Message('A', 'Aman Das', '2026-07-04T10:00:00+05:30', 'The room is reserved.')]
    return RerankedSearch(messages, parser=parser, encoder=FixtureEncoder(), reranker=PairScorer(), cache_dir=None)


def test_pair_relevance_can_replace_a_lexically_similar_question(engine):
    hit = engine.search('Did Priya reserve the room last month?')[0]
    assert hit.id == 'B'
    assert hit.original_text == hit.text == 'The room is reserved.'
    assert hit.ranking['reranker_score'] == .9
    assert hit.hybrid_score == pytest.approx(.85 * .9 + .15 * hit.ranking['first_stage_score'])
    assert 'A' not in engine.last_candidate_ids
    query, rows = engine.reranker.calls[0]
    assert query == 'Did Priya reserve the room last month?'
    assert all(row.sender == 'Priya Shah' for row in rows)


def test_empty_constraints_do_not_run_pair_inference(engine):
    assert engine.search('What did Aman say today?') == []
    assert engine.reranker.calls == []
    assert engine.last_candidate_ids == ()


def test_reranker_never_receives_neighbor_answers_or_label_metadata(engine):
    engine.search('room booking')
    _, rows = engine.reranker.calls[0]
    assert all(type(row) is Message for row in rows)
    assert all(row.text in {'Should we reserve the room?', 'The room is reserved.'} for row in rows)


@pytest.mark.parametrize('bad', [[float('nan')], [-1, -1, -1], [2, 2, 2], [0.5]])
def test_invalid_pair_scores_are_rejected(engine, bad):
    engine.reranker.score = lambda *args: bad
    with pytest.raises(ValueError, match='Reranker'):
        engine.search('room')


@pytest.mark.parametrize('top_k', [0, -1, True, 1.5])
def test_invalid_requested_count(engine, top_k):
    with pytest.raises(ValueError):
        engine.search('room', top_k=top_k)


def test_ties_and_candidate_order_are_stable(engine):
    signals = engine.prepare('room')
    signals = replace(signals, semantic=np.zeros(3), contextual=np.zeros(3), lexical=np.zeros(3))
    engine.reranker.score = lambda query, rows: [.5] * len(rows)
    assert [hit.id for hit in engine.rank(signals, top_k=3)] == ['A', 'B', 'C']


@pytest.mark.parametrize('value', ['{}', '[]', 'null'])
def test_bad_model_manifest_fails_before_loading_files(tmp_path, value):
    (tmp_path / 'download_manifest.json').write_text(value, encoding='utf-8')
    with pytest.raises(ValueError, match='manifest'):
        verify_manifest(tmp_path)
