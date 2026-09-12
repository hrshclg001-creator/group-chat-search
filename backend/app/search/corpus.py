"""Read only original message fields needed for retrieval and display."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

DEFAULT_CORPUS_PATH = Path(__file__).resolve().parents[2] / 'data' / 'messages.jsonl'


@dataclass(frozen=True)
class Message:
    id: str
    sender: str
    timestamp: str
    text: str
    message_type: str = 'text'


def load_corpus(path=DEFAULT_CORPUS_PATH) -> List[Message]:
    messages = []
    seen = set()
    with Path(path).open(encoding='utf-8') as stream:
        for line_number, line in enumerate(stream, 1):
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError('message must be an object')
                fields = {name: record[name] for name in ('id', 'sender', 'timestamp', 'text')}
                if any(not isinstance(value, str) or not value.strip() for value in fields.values()):
                    raise ValueError('required fields must be nonempty strings')
                if fields['id'] in seen:
                    raise ValueError(f"duplicate message ID {fields['id']}")
                if datetime.fromisoformat(fields['timestamp']).utcoffset() is None:
                    raise ValueError('timestamp must be timezone-aware')
                fields['message_type'] = record.get('message_type', 'text')
                if fields['message_type'] not in ('text', 'forwarded', 'url', 'image', 'pdf', 'voice'):
                    raise ValueError('unknown message type')
                messages.append(Message(**fields))
                seen.add(fields['id'])
            except (ValueError, KeyError, TypeError) as exc:
                raise ValueError(f'Invalid corpus line {line_number}: {exc}') from exc
    if not messages:
        raise ValueError('Corpus is empty')
    return messages
