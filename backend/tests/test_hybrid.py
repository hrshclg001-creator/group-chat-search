"""Hybrid routing and score tests use independent, deterministic fixtures."""

from dataclasses import replace

import numpy as np
import pytest

from app.query_understanding import QueryParser
from app.search.constraints import corpus_timezone, understand_constraints
from app.search.corpus import Message
from app.search.hybrid import HybridSearch
from app.search.ranking_config import PROFILES, RankingConfig


class FixtureTokenizer:
    def encode(self, text, add_special_tokens=False):
        return text.split()

    def decode(self, tokens, skip_special_tokens=True):
        return ' '.join(tokens)

    def num_special_tokens_to_add(self, pair=False):
        return 2


class FixtureEncoder:
    tokenizer = FixtureTokenizer()
    max_sequence_length = 256
    settings = {'model': 'constant-vector-fixture'}

    def encode(self, texts):
        return np.ones((len(texts), 2), dtype=np.float32)


@pytest.fixture
def parser():
    return QueryParser({'reference_date': '2026-09-01', 'timezone': 'Asia/Kolkata',
                        'participants': [{'name': 'Priya Sharma'}, {'name': 'Rahul Verma'}, {'name': 'Aman Khan'}]})


@pytest.fixture
def searcher(parser):
    # IDs deliberately do not correspond to chronological order.
    rows = [Message('Z', 'Priya Sharma', '2026-08-31T10:00:00+05:30', 'expense allowance is 500'),
            Message('A', 'Rahul Verma', '2026-08-31T10:01:00+05:30', 'budget details and costs'),
            Message('B', 'Priya Sharma', '2026-07-01T10:00:00+05:30', 'budget details and costs'),
            Message('C', 'Aman Khan', '2026-08-31T20:00:00+05:30', 'done')]
    return HybridSearch(rows, parser=parser, encoder=FixtureEncoder(), cache_dir=None)


@pytest.mark.parametrize('query', [
    'What did Priya say about the budget?', 'Priya ne budget pe kya bola?',
    'message from Priya about costs', 'Priya shared her plan', "Priya's messages about costs",
])
def test_clear_sender_filters_before_top_k(searcher, query):
    hits = searcher.search(query, top_k=10)
    assert len(hits) == 2
    assert {hit.sender for hit in hits} == {'Priya Sharma'}
    assert hits[0].ranking['constraints']['person_mode'] == 'filter'


def test_combined_constraints_exclude_wrong_author_or_month(searcher):
    hits = searcher.search('What did Priya say last month about the budget?', top_k=10)
    assert [hit.id for hit in hits] == ['Z']
    hit = hits[0]
    assert hit.text == hit.original_text == 'expense allowance is 500'
    assert hit.person_match and hit.date_match
    assert hit.ranking['eligible_message_count'] == 1
    # A neighbor need not satisfy the filter, but cannot replace the target.
    assert 'A' in hit.context_message_ids
    assert next(row for row in hit.context_messages if row['is_current'])['id'] == 'Z'


def test_empty_date_intersection_does_not_fall_back(searcher):
    assert searcher.search('What did Priya say today?') == []
    assert searcher.search('What did Aman say in July?') == []


def test_uncertain_person_mentions_use_bonus_not_filter(parser, searcher):
    assert understand_constraints(parser, "Priya's budget limit").person_mode == 'bonus'
    assert len(searcher.search("Priya's budget limit", top_k=10)) == 4
    assert understand_constraints(parser, 'messages about Priya').person_mode == 'none'
    assert understand_constraints(parser, 'birthday for Priya').person_mode == 'none'
    assert understand_constraints(parser, 'What did Priya and Rahul say?').person_mode == 'none'
    assert understand_constraints(parser, 'What did Unknown say?').person_mode == 'none'


@pytest.mark.parametrize('query,start,end,hours', [
    ('messages in late April', '2026-04-21', '2026-04-30', None),
    ('at the start of May', '2026-05-01', '2026-05-07', None),
    ('early February 2024', '2024-02-01', '2024-02-07', None),
    ('mid September', '2026-09-11', '2026-09-20', None),
    ('yesterday morning', '2026-08-31', '2026-08-31', (0, 12)),
    ('in August at night', '2026-08-01', '2026-08-31', (21, 24)),
    ('where did we decide to go for the June trip?', None, None, None),
    ('what was said on March 28 about the June trip?', '2026-03-28', '2026-03-28', None),
    ('messages about the trip in June', None, None, None),
])
def test_message_dates_are_distinct_from_event_dates(parser, query, start, end, hours):
    result = understand_constraints(parser, query)
    assert (result.start_date, result.end_date, result.hour_range) == (start, end, hours)


def test_morning_filter_applies_to_current_timestamp(searcher):
    hits = searcher.search('yesterday morning', top_k=10)
    assert {hit.id for hit in hits} == {'Z', 'A'}


def test_timezone_conversion_handles_midnight_in_india(parser):
    rows = [Message('A', 'Priya Sharma', '2026-08-30T20:00:00+00:00', 'first'),
            Message('B', 'Priya Sharma', '2026-08-30T18:00:00+00:00', 'second')]
    searcher = HybridSearch(rows, parser=parser, encoder=FixtureEncoder(), cache_dir=None)
    assert [hit.id for hit in searcher.search('yesterday')] == ['A']
    with pytest.raises(ValueError, match='Timezone'):
        corpus_timezone('Invalid/NotAZone')


def test_score_breakdown_and_conditional_weights(searcher):
    prepared = searcher.prepare('What did Priya say yesterday?')
    size = len(searcher.messages)
    prepared = replace(prepared, semantic=np.full(size, .8), contextual=np.full(size, .4), lexical=np.full(size, .2))
    hit = searcher.rank(prepared, config=PROFILES['context_first'])[0]
    weights = hit.ranking['weights']
    assert weights['contextual'] == pytest.approx(.45)
    assert weights['semantic'] == pytest.approx(.30)
    assert hit.metadata_bonus == pytest.approx(.1)
    assert hit.hybrid_score == pytest.approx(.45 * .4 + .3 * .8 + .15 * .2 + .1)
    unconstrained = searcher.search('ordinary topic')[0]
    assert unconstrained.ranking['weights'] == searcher.config.weights(False)


def test_lexical_scores_align_by_id_not_index_position(searcher):
    signals = searcher.prepare('budget details')
    expected = {hit.id: hit.lexical_score for hit in searcher.lexical.search('budget details', top_k=10)}
    for index, row in enumerate(searcher.messages):
        assert signals.lexical[index] == expected.get(row.id, 0)


def test_exact_ties_are_stable_and_scores_finite(searcher):
    signals = searcher.prepare('ordinary topic')
    zeros = np.zeros(len(searcher.messages))
    signals = replace(signals, semantic=zeros, contextual=zeros, lexical=zeros)
    hits = searcher.rank(signals, top_k=10)
    assert [hit.id for hit in hits] == ['A', 'B', 'C', 'Z']
    assert all(np.isfinite(hit.hybrid_score) for hit in hits)


@pytest.mark.parametrize('value', [0, -1, True, 1.5])
def test_invalid_k_rejected(searcher, value):
    with pytest.raises(ValueError):
        searcher.search('query', value)


def test_blank_query_and_invalid_type(searcher):
    assert searcher.search('  ') == []
    with pytest.raises(TypeError):
        searcher.search(None)


def test_invalid_weights_rejected():
    with pytest.raises(ValueError):
        RankingConfig('invalid', .5, .5, .5)
    with pytest.raises(ValueError):
        RankingConfig('invalid', float('nan'), .2, .15)
