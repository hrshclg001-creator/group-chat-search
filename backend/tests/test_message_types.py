"""Independent message-type intent, metadata provenance and filter tests."""

import json

import pytest

from app.query_understanding import QueryParser
from app.search.corpus import Message, load_corpus
from app.search.hybrid import HybridSearch
from app.search.message_types import requested_message_type
from app.services.search import SearchService
from test_hybrid import FixtureEncoder


@pytest.mark.parametrize('query,kind', [
    ('Find the first forwarded warning about library hours', 'forwarded'),
    ('What did Priya forward yesterday?', 'forwarded'),
    ('What alert did Rahul Verma forward?', 'forwarded'),
    ('Show me the PDF about the library', 'pdf'),
    ('Find the image of our poster', 'image'),
    ('Where is the voice note about rehearsals?', 'voice'),
    ('Get the link to the recordings', 'url'),
    ('What did Priya say about forwarding the warning?', None),
    ('Who mentioned the forwarded warning?', None),
    ('Find messages that were not forwarded', None),
    ('Show a PDF or image about books', None),
    ('What did Priya not forward?', None),
    ('Show messages discussing the PDF', None),
])
def test_only_explicit_positive_type_requests(query, kind):
    assert requested_message_type(query) == kind


def test_filter_intersects_author_date_and_credits_original_type(tmp_path):
    rows = [Message('A', 'Priya Sharma', '2026-08-20T10:00:00+05:30', 'library warning mentioned'),
            Message('B', 'Rahul Verma', '2026-08-20T10:01:00+05:30', 'library hours changed', 'forwarded'),
            Message('C', 'Priya Sharma', '2026-08-20T10:02:00+05:30', 'library hours changed', 'forwarded'),
            Message('D', 'Priya Sharma', '2026-07-20T10:00:00+05:30', 'library hours changed', 'forwarded')]
    metadata = {'reference_date': '2026-09-01', 'timezone': 'Asia/Kolkata',
                'participants': [{'name': 'Priya Sharma'}, {'name': 'Rahul Verma'}]}
    parser = QueryParser(metadata)
    engine = HybridSearch(rows, parser=parser, encoder=FixtureEncoder(), cache_dir=None)
    service = SearchService(rows, metadata, engine=engine)
    result = service.search('What library warning did Priya forward last month?', 5)
    assert [hit.matching_message.id for hit in result.results] == ['C']
    assert result.results[0].matching_message.text == 'library hours changed'
    assert result.interpreted_query.message_type == 'forwarded'
    assert result.results[0].query_metadata.message_type == 'forwarded'
    assert service.search('What did Rahul forward in July?', 5).results == []
    assert service.search('Find the PDF', 5).results == []


def test_loader_retains_type_without_reading_topic_or_thread(tmp_path):
    path = tmp_path / 'rows.jsonl'
    record = {'id': 'A', 'sender': 'Test Student', 'timestamp': '2026-04-01T10:00:00+05:30',
              'text': 'No literal forward marker', 'message_type': 'forwarded',
              'thread_id': 'DO_NOT_INDEX', 'metadata': {'topic': 'DO_NOT_INDEX'}}
    path.write_text(json.dumps(record), encoding='utf-8')
    loaded = load_corpus(path)[0]
    assert loaded.message_type == 'forwarded'
    assert not hasattr(loaded, 'thread_id')
    record['message_type'] = 'invalid'
    path.write_text(json.dumps(record), encoding='utf-8')
    with pytest.raises(ValueError, match='message type'):
        load_corpus(path)
