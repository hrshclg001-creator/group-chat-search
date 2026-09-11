"""Smoke checks for the health contract and local CORS policy."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.parametrize('origin', [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
])
def test_local_frontend_cors(client, origin):
    response = client.get('/api/health', headers={'Origin': origin})
    assert response.headers['access-control-allow-origin'] == origin

    preflight = client.options('/api/health', headers={
        'Origin': origin,
        'Access-Control-Request-Method': 'GET',
    })
    assert preflight.status_code == 200
    assert preflight.headers['access-control-allow-origin'] == origin


def test_unlisted_origin_is_not_allowed(client):
    response = client.get('/api/health', headers={'Origin': 'https://example.com'})
    assert 'access-control-allow-origin' not in response.headers


def test_search_is_not_implemented(client):
    assert client.get('/api/search').status_code == 404
