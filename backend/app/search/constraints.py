"""Resolve ranking constraints without treating every name/date as a filter."""

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..query_understanding.dates import ENDPOINT, MONTH, parse_dates
from ..query_understanding.parser import normalize
from .ranking_config import DAY_PARTS, MONTH_PARTS


def corpus_timezone(name):
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        # Windows may not ship an IANA database. The modern synthetic corpus
        # uses Indian Standard Time throughout; no machine-local fallback.
        if name in ('Asia/Kolkata', 'Asia/Calcutta'):
            return timezone(timedelta(hours=5, minutes=30), name)
        if name == 'UTC':
            return timezone.utc
        raise ValueError(f'Timezone database unavailable for {name}')


@dataclass(frozen=True)
class Constraints:
    parsed_query: dict
    person: object
    person_mode: str
    start_date: object
    end_date: object
    hour_range: object
    reasons: tuple

    @property
    def has_filter(self):
        return self.person_mode == 'filter' or self.start_date is not None

    def to_dict(self):
        return asdict(self)


def understand_constraints(parser, query):
    parsed = parser.parse(query)
    text = normalize(query).replace('\u2019', "'")
    reasons = []
    person = parsed.person
    mode = 'none'
    if person:
        aliases = [alias for alias, names in parser.aliases.items() if names == {person}]
        alias = '(?:' + '|'.join(re.escape(value) for value in sorted(aliases, key=len, reverse=True)) + ')'
        # A conjunction immediately following the name is not a single sender.
        named = rf'(?<!\w){alias}(?!\w)(?!\s+(?:and|or|aur)\b)'
        clear_sender = any(re.search(pattern, text) for pattern in (
            rf'\bdid\s+{named}', rf'\bfrom\s+{named}', rf'{named}\s+ne\b',
            rf'{named}\s+(?:said|shared|sent|forwarded|wrote|asked|replied|suggested|proposed|confirmed)\b',
            rf'{named}\s+was\s+(?:asking|saying|suggesting|sharing)\b',
            rf"{named}'s\s+(?:messages?|notes?|replies|updates?)\b",
        ))
        topic_mention = re.search(rf'\b(?:about|to|for)\s+{named}', text)
        if clear_sender:
            mode = 'filter'
            reasons.append('Explicit sender language: require the current message author.')
        elif not topic_mention:
            mode = 'bonus'
            reasons.append('Known person mention without a clear sender role: bonus only.')
        else:
            reasons.append('Person appears as a topic/recipient: no sender preference.')
    elif parsed.person_candidates:
        reasons.append('Ambiguous/multiple names: no sender filter or bonus.')

    # Strip only a date immediately attached to an event noun before deciding
    # chat-time constraints. Other dates in the same query still apply.
    event = r'(?:trip|holiday|vacation|birthday|party|exam|event|hackathon|journey)'
    event_date = re.compile(rf'(?<!\w)(?:{ENDPOINT})\s+{event}\b|\b{event}\s+(?:in|on|for)\s+(?:{ENDPOINT})(?!\w)')
    chat_time_text = event_date.sub(' ', text)
    if chat_time_text != text:
        reasons.append('Date attached to an event is not treated as the message timestamp.')
    start, end, warnings = parse_dates(chat_time_text, parser.reference_date)
    hour_range = None
    if start:
        first, last = date.fromisoformat(start), date.fromisoformat(end)
        if (first.year, first.month) == (last.year, last.month):
            qualifier = re.search(rf'\b(early|start|mid|late)(?:\s+of)?\s+({MONTH})\b', chat_time_text)
            if qualifier:
                low, high = MONTH_PARTS[qualifier[1]]
                start = first.replace(day=max(first.day, low)).isoformat()
                end = last.replace(day=min(last.day, high)).isoformat()
                if start > end:
                    start = end = None
                    warnings += ('Month-part qualifier conflicts with the requested dates.',)
        parts = [name for name in DAY_PARTS if re.search(rf'\b{name}\b', chat_time_text)]
        if len(parts) == 1:
            hour_range = DAY_PARTS[parts[0]]
        elif len(parts) > 1:
            reasons.append('Multiple day parts: retaining the full date interval.')
        if start:
            reasons.append('Resolved chat-date bounds: exclude current messages outside the interval.')
    reasons.extend(warnings)
    if warnings:
        start = end = hour_range = None
    return Constraints(parsed.to_dict(), person, mode, start, end, hour_range, tuple(reasons))


def local_message_time(message, tz):
    stamp = datetime.fromisoformat(message.timestamp)
    if stamp.utcoffset() is None:
        raise ValueError('Message timestamps must be timezone-aware')
    return stamp.astimezone(tz)
