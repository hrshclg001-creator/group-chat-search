"""Real pairwise inference stays local; tests never download model files."""

import pytest

from app.search.corpus import Message
from app.search.reranked import LocalReranker
from app.search.reranker_config import MODEL_DIRECTORY


@pytest.mark.skipif(not (MODEL_DIRECTORY / 'download_manifest.json').exists(),
                    reason='Run scripts.prepare_reranker for offline integration checks')
def test_local_reranker_prefers_an_answer_to_unrelated_chatter():
    reranker = LocalReranker()
    messages = [Message('FIXTURE_A', 'Student', '2026-08-01T10:00:00+05:30',
                        'The seminar starts at six in the auditorium.'),
                Message('FIXTURE_B', 'Student', '2026-08-01T10:01:00+05:30',
                        'I had noodles for lunch today.')]
    scores = reranker.score('When does the seminar begin?', messages)
    assert len(scores) == 2 and scores[0] > scores[1]
    assert all(0 <= score <= 1 for score in scores)
