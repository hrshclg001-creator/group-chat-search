"""Optional real-model checks: use the local cache, never download in tests."""

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from app.search.corpus import Message
from app.search.embedding import LocalEncoder
from app.search.model_config import MODEL_DIRECTORY
from app.search.semantic import SemanticSearch

pytestmark = pytest.mark.skipif(not (MODEL_DIRECTORY / 'download_manifest.json').exists(),
                                reason='Run scripts.prepare_model to enable offline model integration checks')


@pytest.fixture(scope='module')
def encoder():
    return LocalEncoder()


@pytest.mark.parametrize('reply', ['done', 'haan pakka', 'this one', 'ok final'])
def test_real_model_disambiguates_identical_short_text_representations(encoder, reply):
    texts = ['We chose an indoor restaurant for dinner.', reply, 'I will reserve the table.',
             'The coding exercise needs a binary search.', reply, 'Run the algorithm on sorted input.']
    start = datetime(2026, 3, 1, 10, tzinfo=timezone.utc)
    messages = [Message(f'MSG_{i + 1:06d}', 'Student',
                        (start + timedelta(minutes=i if i < 3 else 120 + i)).isoformat(), text)
                for i, text in enumerate(texts)]
    searcher = SemanticSearch(messages, contextual=True, encoder=encoder, cache_dir=None)
    assert searcher.contexts[1].original_text == searcher.contexts[4].original_text == reply
    assert not np.allclose(searcher.matrix[1], searcher.matrix[4], atol=1e-6)
    for hit in searcher.search('restaurant dinner reservation', top_k=6):
        source = next(row for row in messages if row.id == hit.id)
        assert hit.text == hit.original_text == source.text
