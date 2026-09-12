"""Bounded chronological context, always anchored to an original message."""

from dataclasses import dataclass
from datetime import datetime

from .corpus import Message


@dataclass(frozen=True)
class ContextRecord:
    current: Message
    messages: tuple
    context_text: str

    @property
    def original_text(self):
        return self.current.text

    @property
    def context_message_ids(self):
        return tuple(message.id for message in self.messages)


def format_context(current_id, messages, texts=None):
    current_index = next(i for i, message in enumerate(messages) if message.id == current_id)
    lines = []
    for index, message in enumerate(messages):
        label = 'Current message' if index == current_index else (
            'Previous message' if index < current_index else 'Following message')
        text = message.text if texts is None else texts[index]
        if text:
            lines.append(f'{label}: {text}')
    return '\n'.join(lines)


def build_contexts(messages, window_size=2, max_gap_seconds=1800):
    if type(window_size) is not int or not 0 <= window_size <= 2:
        raise ValueError('Context window must be between zero and two messages per side')
    if not 0 < max_gap_seconds <= 1800:
        raise ValueError('Context time cutoff must be between zero and 1800 seconds')
    rows = sorted(messages, key=lambda row: (datetime.fromisoformat(row.timestamp), row.id))
    if not rows or len({row.id for row in rows}) != len(rows):
        raise ValueError('Context requires nonempty messages with unique IDs')
    stamps = [datetime.fromisoformat(row.timestamp) for row in rows]
    if any(stamp.utcoffset() is None for stamp in stamps):
        raise ValueError('Context timestamps must be timezone-aware')
    contexts = []
    for index, current in enumerate(rows):
        indices = range(max(0, index - window_size), min(len(rows), index + window_size + 1))
        neighbors = tuple(rows[i] for i in indices
                          if abs((stamps[i] - stamps[index]).total_seconds()) <= max_gap_seconds)
        contexts.append(ContextRecord(current, neighbors, format_context(current.id, neighbors)))
    return contexts


def fit_context_to_budget(record, tokenizer, max_sequence_length):
    """Prioritize the current message; trim longest neighbors before its text.

    Full originals and full bounded context remain untouched in ContextRecord.
    The returned string is the exact, separately recorded embedding input.
    """
    budget = max_sequence_length - tokenizer.num_special_tokens_to_add(pair=False)
    if budget < 8:
        raise ValueError('Embedding token budget is too small')
    if len(tokenizer.encode(record.context_text, add_special_tokens=False)) <= budget:
        return record.context_text, []
    current_index = next(i for i, row in enumerate(record.messages) if row.id == record.current.id)
    tokens = [tokenizer.encode(row.text, add_special_tokens=False) for row in record.messages]
    original_lengths = [len(ids) for ids in tokens]
    while True:
        texts = [tokenizer.decode(ids, skip_special_tokens=True) if ids else '' for ids in tokens]
        rendered = format_context(record.current.id, record.messages, texts)
        excess = len(tokenizer.encode(rendered, add_special_tokens=False)) - budget
        if excess <= 0:
            break
        candidates = [i for i, ids in enumerate(tokens) if i != current_index and ids]
        chosen = max(candidates, key=lambda i: (len(tokens[i]), -i)) if candidates else current_index
        if not tokens[chosen]:
            raise ValueError('Cannot fit current-message marker in the embedding budget')
        del tokens[chosen][-min(len(tokens[chosen]), max(1, excess)):]
    truncated_ids = [row.id for i, row in enumerate(record.messages) if len(tokens[i]) < original_lengths[i]]
    return rendered, truncated_ids
