"""Validate corpus structure, coverage and audit metadata without retrieval code."""

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from .corpus_config import END_DATE, IST, MESSAGE_TYPES, PARTICIPANTS, START_DATE, THREAD_IDS

DEFAULT_DATA = Path(__file__).resolve().parents[1] / 'data'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_corpus(messages, metadata):
    from .generate_data import encode_messages, message_type

    require(len(messages) >= 4200, 'Expected at least 4200 messages')
    require(metadata.get('participants') == PARTICIPANTS, 'Expected exactly the eight configured participants')
    participant_names = {person['id']: person['name'] for person in PARTICIPANTS}
    required = {'id', 'timestamp', 'sender', 'text', 'message_type'}
    timestamps = []
    for number, row in enumerate(messages, 1):
        require(required <= row.keys(), 'Missing required message fields')
        require(row['id'] == f'MSG_{number:06d}', 'IDs must be unique, stable and sequential')
        require(isinstance(row['text'], str) and bool(row['text'].strip()), 'Text must be nonempty')
        require(row['message_type'] in MESSAGE_TYPES, 'Unknown message type')
        require(row['message_type'] == message_type(row['text']), 'Message type does not match content')
        details = row.get('metadata', {})
        require(details.get('participant_id') in participant_names, 'Unknown participant ID')
        require(row['sender'] == participant_names[details['participant_id']], 'Sender name and ID mismatch')
        require(bool(details.get('topic')) and bool(details.get('episode_id')), 'Missing episode/topic metadata')
        stamp = datetime.fromisoformat(row['timestamp'])
        require(stamp.utcoffset() == IST.utcoffset(None), 'Timestamps must use +05:30')
        require(START_DATE <= stamp.date() <= END_DATE, 'Timestamp outside corpus dates')
        timestamps.append(stamp)
        require(row.get('thread_id') is None or row['thread_id'] in THREAD_IDS, 'Unknown decision thread')
    require(len({row['id'] for row in messages}) == len(messages), 'Duplicate IDs')
    require({row['sender'] for row in messages} == set(participant_names.values()), 'Not all eight participants speak')
    require(timestamps == sorted(timestamps), 'Messages must be chronological')
    require(timestamps[0].date() == START_DATE and timestamps[-1].date() == END_DATE, 'Missing boundary dates')
    require(timestamps[-1] - timestamps[0] >= timedelta(days=183), 'Corpus must span roughly six months')
    require({stamp.month for stamp in timestamps} == set(range(3, 9)), 'Missing month')
    require(len({stamp.date() for stamp in timestamps}) == 184, 'Missing daily coverage')
    require(metadata.get('message_count') == len(messages), 'Metadata count mismatch')
    require(metadata.get('corpus_start') == messages[0]['timestamp'], 'Metadata start mismatch')
    require(metadata.get('corpus_end') == messages[-1]['timestamp'], 'Metadata end mismatch')
    require(metadata.get('reference_date') == '2026-09-01', 'Reference date must be fixed')
    require(metadata.get('synthetic') is True, 'Corpus must be marked synthetic')
    require(metadata.get('sha256') == hashlib.sha256(encode_messages(messages)).hexdigest(), 'Corpus hash mismatch')
    require(metadata.get('message_type_counts') == dict(Counter(row['message_type'] for row in messages)), 'Type counts mismatch')
    require(metadata.get('topic_counts') == dict(Counter(row['metadata']['topic'] for row in messages)), 'Topic counts mismatch')

    types = {row['message_type'] for row in messages}
    require(types == MESSAGE_TYPES, 'Missing required message varieties')
    texts = [row['text'] for row in messages]
    for token in ['haan', 'done', 'ok', '😂']:
        require(token in texts, f'Missing short reply: {token}')
    combined = '\n'.join(texts)
    for marker in ['[Image]', '[PDF]', '[Voice message]', 'Forwarded:', 'https://']:
        require(marker in combined, f'Missing variety: {marker}')
    require(any(re.search(r'\b(hai|nahi|kya|yaar|mat)\b', text) for text in texts), 'Missing Hinglish')
    require(any(word in combined for word in ['thnks', 'nhi', 'sorryyy', 'birhtday']), 'Missing typos')
    require({'random', 'college', 'travel', 'assignments', 'exams', 'movies', 'food', 'coding', 'events'}
            <= {row['metadata']['topic'] for row in messages}, 'Missing conversation topics')

    require(metadata.get('decision_thread_ids') == list(THREAD_IDS), 'Decision thread IDs mismatch')
    require(set(metadata.get('decision_threads', {})) == set(THREAD_IDS), 'Missing thread audit metadata')
    by_id = {row['id']: row for row in messages}
    for thread_id in THREAD_IDS:
        rows = [row for row in messages if row.get('thread_id') == thread_id]
        require(len(rows) >= 60, f'{thread_id} is missing or too short')
        details = metadata['decision_threads'][thread_id]
        require(details['message_count'] == len(rows), 'Thread count mismatch')
        require(details['message_ids'] == [row['id'] for row in rows], 'Thread membership mismatch')
        require(details['first_message_id'] == rows[0]['id'] and details['last_message_id'] == rows[-1]['id'], 'Thread ID range mismatch')
        require(details['start'] == rows[0]['timestamp'] and details['end'] == rows[-1]['timestamp'], 'Thread time range mismatch')
        episodes = {row['metadata']['episode_id'] for row in rows}
        require(details['episode_count'] == len(episodes) >= 6, 'Thread needs six episodes')
        days = {row['timestamp'][:10] for row in rows}
        require(len(days) >= 6, 'Thread must occur across several dates')
        require(datetime.fromisoformat(rows[-1]['timestamp']) - datetime.fromisoformat(rows[0]['timestamp']) >= timedelta(days=14), 'Thread span too short')
        require(len({row['sender'] for row in rows}) == 8, 'Decision thread must involve everyone')
        conclusion = by_id.get(details['conclusion_message_id'])
        require(conclusion is not None and conclusion.get('thread_id') == thread_id, 'Invalid conclusion reference')
        require(rows[0]['id'] < conclusion['id'] < rows[-1]['id'], 'Conclusion needs discussion and follow-up')
        require(any(rows[0]['timestamp'] < row['timestamp'] < rows[-1]['timestamp']
                    and row.get('thread_id') != thread_id for row in messages), 'Missing intervening background chatter')
    return {'message_count': len(messages), 'participants': len(participant_names), 'days': 184,
            'thread_counts': {key: metadata['decision_threads'][key]['message_count'] for key in THREAD_IDS}}


def validate_files(data_dir=DEFAULT_DATA):
    data_dir = Path(data_dir)
    raw = (data_dir / 'messages.jsonl').read_bytes()
    metadata = json.loads((data_dir / 'corpus_metadata.json').read_text(encoding='utf-8'))
    require(hashlib.sha256(raw).hexdigest() == metadata.get('sha256'), 'On-disk corpus hash mismatch')
    messages = [json.loads(line) for line in raw.decode('utf-8').splitlines()]
    return validate_corpus(messages, metadata)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=DEFAULT_DATA)
    args = parser.parse_args()
    print(json.dumps(validate_files(args.data_dir), indent=2))


if __name__ == '__main__':
    main()
