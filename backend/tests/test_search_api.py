"""HTTP contracts and lifespan/index reuse with a deterministic local encoder."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
import numpy as np
import pytest

from app.main import create_app
from app.query_understanding import QueryParser
from app.search.corpus import Message
from app.search.hybrid import HybridSearch
from app.services.conversation import ConversationContext
from app.services.search import SearchService


class CountingEncoder:
    max_sequence_length = 256
    settings = {'model': 'api-test-fixture'}

    def __init__(self):
        self.calls = []
        self.tokenizer = self

    def encode(self, texts, add_special_tokens=None):
        if isinstance(texts, str):
            return texts.split()
        self.calls.append(list(texts))
        return np.ones((len(texts), 2), dtype=np.float32)

    def num_special_tokens_to_add(self, pair=False):
        return 2

    def decode(self, tokens, skip_special_tokens=True):
        return ' '.join(tokens)


@pytest.fixture
def fixture_data():
    metadata = {'reference_date': '2026-09-01', 'timezone': 'Asia/Kolkata',
                'participants': [{'name': 'Aarav Sharma'}, {'name': 'Ananya Verma'}]}
    start = datetime(2026, 8, 31, 10, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    messages = [Message(f'MSG_{i:06d}', metadata['participants'][i % 2]['name'],
                        (start + timedelta(minutes=i)).isoformat(), 'pizza' if i == 3 else f'ordinary reply {i}')
                for i in range(8)]
    return messages, metadata


@pytest.fixture
def setup(fixture_data):
    messages, metadata = fixture_data
    encoder = CountingEncoder()
    factories = []

    def factory():
        engine = HybridSearch(reversed(messages), parser=QueryParser(metadata), encoder=encoder, cache_dir=None)
        service = SearchService(reversed(messages), metadata, engine)
        factories.append(service)
        return service

    application = create_app(factory)
    with TestClient(application) as client:
        yield client, factories, encoder, messages
    assert not hasattr(application.state, 'search_service')


def test_search_returns_original_match_and_three_chronological_neighbors(setup):
    client, factories, _, messages = setup
    body = client.post('/api/search', json={'query': 'pizza', 'top_k': 1}).json()
    assert body['query'] == 'pizza'
    assert body['search_time_ms'] >= 0
    hit = body['results'][0]
    assert hit['matching_message'] == {'id': messages[3].id, 'sender': messages[3].sender,
                                       'timestamp': messages[3].timestamp, 'text': 'pizza'}
    assert [row['id'] for row in hit['previous_messages']] == [row.id for row in messages[:3]]
    assert [row['id'] for row in hit['next_messages']] == [row.id for row in messages[4:7]]
    assert hit['rank'] == 1
    assert hit['query_metadata'] == body['interpreted_query']
    assert body['interpreted_query']['reference_date'] == '2026-09-01'
    direct = factories[0].engine.search('pizza', top_k=1)[0]
    assert hit['matching_message']['id'] == direct.id
    assert hit['search_score'] == direct.hybrid_score
    assert hit['semantic_score'] == direct.semantic_score
    assert hit['contextual_score'] == direct.contextual_score
    assert hit['lexical_score'] == direct.lexical_score
    # Display grows to three per side without changing the embedding window.
    assert len(direct.context_message_ids) == 5


def test_api_reuses_indexes_and_encodes_only_queries_per_request(setup):
    client, factories, encoder, _ = setup
    assert len(factories) == 1
    service = factories[0]
    original_matrix = service.engine.semantic.matrix
    context_matrix = service.engine.contextual.matrix
    calls_at_start = len(encoder.calls)
    assert calls_at_start == 2  # Corpus original and contextual embeddings, at startup.
    for query in ('pizza', 'What did Ananya say yesterday?'):
        assert client.post('/api/search', json={'query': query}).status_code == 200
    assert encoder.calls[calls_at_start:] == [['pizza'], ['What did Ananya say yesterday?']]
    assert len(factories) == 1
    assert service.engine.semantic.matrix is original_matrix
    assert service.engine.contextual.matrix is context_matrix


def test_metadata_filters_and_rank_order_match_direct_engine(setup):
    client, factories, _, _ = setup
    query = 'What did Ananya say yesterday morning?'
    response = client.post('/api/search', json={'query': query, 'top_k': 3})
    assert response.status_code == 200
    body = response.json()
    interpreted = body['interpreted_query']
    assert interpreted['person'] == 'Ananya Verma'
    assert interpreted['person_mode'] == 'filter'
    assert interpreted['start_date'] == interpreted['end_date'] == '2026-08-31'
    assert interpreted['hour_range'] == [0, 12]
    assert [hit['rank'] for hit in body['results']] == [1, 2, 3]
    assert all(hit['matching_message']['sender'] == 'Ananya Verma' for hit in body['results'])
    assert [hit['matching_message']['id'] for hit in body['results']] == [
        hit.id for hit in factories[0].engine.search(query, top_k=3)]


def test_empty_result_retains_interpretation(setup):
    client, _, _, _ = setup
    response = client.post('/api/search', json={'query': 'What did Aarav say today?'})
    assert response.status_code == 200
    assert response.json()['results'] == []
    assert response.json()['interpreted_query']['start_date'] == '2026-09-01'


def test_event_date_interpretation_reports_effective_filter(setup):
    client, _, _, _ = setup
    body = client.post('/api/search', json={'query': 'What did we decide for the June trip?'}).json()
    assert body['interpreted_query']['start_date'] is None
    assert body['interpreted_query']['intent'] == 'semantic'
    assert any('event' in reason for reason in body['interpreted_query']['explanations'])


@pytest.mark.parametrize('payload', [
    {}, {'query': ''}, {'query': '  \n\t'}, {'query': 42}, {'query': None},
    {'query': 'a' * 2001}, {'query': 'a', 'top_k': 0}, {'query': 'a', 'top_k': 51},
    {'query': 'a', 'top_k': -1}, {'query': 'a', 'top_k': True},
    {'query': 'a', 'top_k': 1.5}, {'query': 'a', 'top_k': '5'},
    {'query': 'a', 'unknown_field': 'unsupported'},
])
def test_invalid_payload_returns_422_without_inference(setup, payload):
    client, _, encoder, _ = setup
    count = len(encoder.calls)
    assert client.post('/api/search', json=payload).status_code == 422
    assert len(encoder.calls) == count


def test_default_top_k_and_raw_query_preserved(setup):
    client, _, _, _ = setup
    body = client.post('/api/search', json={'query': '  pizza  '}).json()
    assert body['query'] == body['interpreted_query']['raw_query'] == '  pizza  '
    assert len(body['results']) == 5


def test_stats_uses_loaded_corpus_without_encoding(setup):
    client, _, encoder, messages = setup
    count = len(encoder.calls)
    response = client.get('/api/stats')
    assert response.status_code == 200
    assert response.json() == {
        'message_count': 8, 'participant_count': 2,
        'date_range': {'start': messages[0].timestamp, 'end': messages[-1].timestamp},
        'reference_date': '2026-09-01', 'timezone': 'Asia/Kolkata'}
    assert len(encoder.calls) == count


@pytest.mark.parametrize('origin', ['http://localhost:5173', 'http://127.0.0.1:5173'])
def test_search_post_cors_preflight_and_response(setup, origin):
    client, _, _, _ = setup
    preflight = client.options('/api/search', headers={
        'Origin': origin, 'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type'})
    assert preflight.status_code == 200
    assert preflight.headers['access-control-allow-origin'] == origin
    response = client.post('/api/search', json={'query': 'pizza'}, headers={'Origin': origin})
    assert response.headers['access-control-allow-origin'] == origin


def test_missing_model_keeps_stats_and_health_and_does_not_retry(fixture_data, monkeypatch):
    messages, metadata = fixture_data
    calls = []
    from app.search import hybrid

    def missing(*args, **kwargs):
        calls.append(True)
        raise FileNotFoundError('missing local model')

    monkeypatch.setattr(hybrid, 'HybridSearch', missing)
    # Exercise the production factory with real corpus/stats but no model.
    with TestClient(create_app()) as client:
        for _ in range(2):
            response = client.post('/api/search', json={'query': 'trip'})
            assert response.status_code == 503
            assert 'prepare_model' in response.json()['detail']
            assert client.get('/api/health').status_code == 200
            assert client.get('/api/stats').json()['message_count'] >= 4000
    assert calls == [True]


def test_display_context_boundaries_gaps_and_equal_timestamp_order(fixture_data):
    messages, _ = fixture_data
    context = ConversationContext(reversed(messages))
    assert context.around(messages[0].id)[1] == ()
    assert context.around(messages[-1].id)[2] == ()
    assert context.around(messages[0].id)[2] == tuple(messages[1:4])
    far = Message('FAR', 'Aarav Sharma', '2026-09-01T00:00:00+05:30', 'new day')
    assert ConversationContext([*messages, far]).around(far.id)[1] == ()
    tied = [Message(name, 'Aarav Sharma', messages[0].timestamp, name) for name in ('Z', 'A', 'M')]
    current, previous, following = ConversationContext(tied).around('M')
    assert current.id == 'M'
    assert [row.id for row in previous + (current,) + following] == ['A', 'M', 'Z']


def test_openapi_documents_both_contracts(setup):
    client, _, _, _ = setup
    schema = client.get('/openapi.json').json()
    assert 'post' in schema['paths']['/api/search']
    assert 'get' in schema['paths']['/api/stats']
    assert 'SearchResponse' in schema['components']['schemas']
