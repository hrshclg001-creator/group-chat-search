"""Metadata-driven participant matching and deterministic calendar parsing."""

from dataclasses import asdict, dataclass
from datetime import date
import json
from pathlib import Path
import re
from typing import Optional, Tuple
import unicodedata

from .dates import parse_dates


DEFAULT_METADATA_PATH = Path(__file__).resolve().parents[2] / 'data' / 'corpus_metadata.json'


def normalize(text):
    return ' '.join(unicodedata.normalize('NFKC', text).casefold().split())


@dataclass(frozen=True)
class ParsedQuery:
    raw_query: str
    person: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    intent: str
    reference_date: str
    timezone: str
    person_candidates: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    def to_dict(self):
        result = asdict(self)
        result['person_candidates'] = list(self.person_candidates)
        result['warnings'] = list(self.warnings)
        return result


class QueryParser:
    """Parse known name mentions and explicit time expressions, without ranking.

    Unique full/first/last names resolve to the metadata's canonical full name.
    Several distinct names remain candidates, not an arbitrary sender filter.
    """

    def __init__(self, metadata):
        if not isinstance(metadata, dict):
            raise ValueError('Corpus metadata must be an object')
        reference = metadata.get('reference_date')
        if not isinstance(reference, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', reference):
            raise ValueError('Corpus metadata requires an explicit ISO reference_date')
        self.reference_date = date.fromisoformat(reference)
        self.timezone = metadata.get('timezone')
        if not isinstance(self.timezone, str) or not self.timezone.strip():
            raise ValueError('Corpus metadata requires a timezone')
        participants = metadata.get('participants')
        if not isinstance(participants, list) or not participants:
            raise ValueError('Corpus metadata requires participants')
        self.aliases = {}
        self.names = []
        normalized_names = set()
        for participant in participants:
            name = participant.get('name') if isinstance(participant, dict) else None
            if not isinstance(name, str) or not name.strip():
                raise ValueError('Each participant requires a nonempty name')
            full = normalize(name)
            if full in normalized_names:
                raise ValueError('Participant names must be unique')
            normalized_names.add(full)
            self.names.append(name)
            for alias in {full, full.split()[0], full.split()[-1]}:
                self.aliases.setdefault(alias, set()).add(name)

    @classmethod
    def from_metadata(cls, path=DEFAULT_METADATA_PATH):
        with Path(path).open(encoding='utf-8') as stream:
            return cls(json.load(stream))

    def parse(self, query):
        if not isinstance(query, str):
            raise TypeError('query must be a string')
        text = normalize(query)
        matched = set()
        occupied = []
        # Longest aliases take precedence, so a full name disambiguates a
        # shared first/last name inside that same span.
        for alias in sorted(self.aliases, key=lambda value: (-len(value), value)):
            for match in re.finditer(rf'(?<!\w){re.escape(alias)}(?!\w)', text):
                if any(match.start() < end and match.end() > start for start, end in occupied):
                    continue
                occupied.append(match.span())
                matched.update(self.aliases[alias])
        candidates = tuple(name for name in self.names if name in matched)
        person = candidates[0] if len(candidates) == 1 else None
        warnings = ('Multiple or ambiguous participants; no single person was selected.',) if len(candidates) > 1 else ()
        start, end, date_warnings = parse_dates(text, self.reference_date)
        intent = ('person_' if person else '') + ('time_' if start else '') + 'semantic'
        return ParsedQuery(query, person, start, end, intent,
                           self.reference_date.isoformat(), self.timezone, candidates,
                           warnings + date_warnings)
