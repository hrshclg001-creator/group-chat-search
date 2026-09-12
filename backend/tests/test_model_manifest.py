"""Malformed cached metadata must fail safely, without inference or download."""

import json

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.search import embedding
from app.search.model_config import MODEL_FILES, MODEL_ID, MODEL_REVISION, validate_model_manifest
from scripts import prepare_model


def manifest():
    return {'model_id': MODEL_ID, 'revision': MODEL_REVISION,
            'sha256': {name: 'a' * 64 for name in MODEL_FILES}}


@pytest.mark.parametrize('bad', [
    None, [], {},
    {**manifest(), 'revision': 'different'},
    {**manifest(), 'sha256': None},
    {**manifest(), 'sha256': {name: 'invalid' for name in MODEL_FILES}},
    {**manifest(), 'sha256': {name: 123 for name in MODEL_FILES}},
    {**manifest(), 'sha256': {**manifest()['sha256'], '../unexpected': 'a' * 64}},
])
def test_malformed_manifest_rejected_by_loader_and_preparation(tmp_path, monkeypatch, bad):
    for name in MODEL_FILES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'placeholder')
    (tmp_path / 'download_manifest.json').write_text(json.dumps(bad), encoding='utf-8')
    monkeypatch.setattr(embedding, 'MODEL_DIRECTORY', tmp_path)
    monkeypatch.setattr(prepare_model, 'MODEL_DIRECTORY', tmp_path)
    def no_network(*args, **kwargs):
        raise AssertionError('A malformed cache must not trigger an implicit download')
    monkeypatch.setattr(prepare_model.urllib.request, 'urlopen', no_network)
    for action in (embedding.LocalEncoder, prepare_model.prepare_model):
        with pytest.raises(ValueError, match='Invalid local model manifest'):
            action()


def test_valid_manifest_schema_accepted():
    validate_model_manifest(manifest())


def test_corrupt_manifest_keeps_api_alive_with_search_unavailable(tmp_path, monkeypatch):
    for name in MODEL_FILES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'placeholder')
    (tmp_path / 'download_manifest.json').write_text('{}', encoding='utf-8')
    monkeypatch.setattr(embedding, 'MODEL_DIRECTORY', tmp_path)
    with TestClient(create_app()) as client:
        assert client.get('/api/health').status_code == 200
        assert client.get('/api/stats').json()['message_count'] == 4634
        response = client.post('/api/search', json={'query': 'library opening hours'})
        assert response.status_code == 503
        assert 'prepare_model' in response.json()['detail']
