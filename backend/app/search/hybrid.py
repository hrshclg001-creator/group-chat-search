"""Hybrid cosine/TF-IDF ranking with explicit author and chat-date constraints."""

from dataclasses import asdict, dataclass

import numpy as np

from ..query_understanding import QueryParser
from .constraints import corpus_timezone, local_message_time, understand_constraints
from .embedding import LocalEncoder, normalize_vectors
from .lexical import LexicalSearch
from .model_config import EMBEDDING_CACHE
from .ranking_config import DAY_PARTS, DEFAULT_CONFIG, MONTH_PARTS
from .semantic import SemanticSearch


@dataclass(frozen=True)
class QuerySignals:
    constraints: object
    semantic: np.ndarray
    contextual: np.ndarray
    lexical: np.ndarray
    person_match: np.ndarray
    date_match: np.ndarray
    eligible: np.ndarray


@dataclass(frozen=True)
class HybridResult:
    id: str
    sender: str
    timestamp: str
    text: str
    original_text: str
    hybrid_score: float
    semantic_score: float
    contextual_score: float
    lexical_score: float
    person_match: bool
    date_match: bool
    metadata_bonus: float
    context_text: str
    context_message_ids: tuple
    context_messages: tuple
    ranking: dict

    def to_dict(self):
        return asdict(self)


class HybridSearch:
    def __init__(self, messages, *, parser=None, encoder=None, cache_dir=EMBEDDING_CACHE,
                 config=DEFAULT_CONFIG):
        messages = tuple(messages)
        self.parser = parser if parser is not None else QueryParser.from_metadata()
        self.config = config
        self.encoder = encoder if encoder is not None else LocalEncoder()
        self.semantic = SemanticSearch(messages, encoder=self.encoder, cache_dir=cache_dir)
        self.contextual = SemanticSearch(messages, contextual=True, encoder=self.encoder, cache_dir=cache_dir)
        self.lexical = LexicalSearch(messages)
        self.contexts = self.contextual.contexts
        self.messages = tuple(record.current for record in self.contexts)
        if [record.current.id for record in self.semantic.contexts] != [row.id for row in self.messages]:
            raise ValueError('Semantic and contextual index IDs are misaligned')
        self.id_to_index = {message.id: index for index, message in enumerate(self.messages)}
        tz = corpus_timezone(self.parser.timezone)
        self.local_times = tuple(local_message_time(message, tz) for message in self.messages)

    def prepare(self, query):
        if not isinstance(query, str):
            raise TypeError('query must be a string')
        if not query.strip():
            return None
        constraints = understand_constraints(self.parser, query)
        vector = normalize_vectors(self.encoder.encode([query]))[0]
        semantic = np.clip(self.semantic.matrix @ vector, 0, 1)
        contextual = np.clip(self.contextual.matrix @ vector, 0, 1)
        lexical = np.zeros(len(self.messages), dtype=np.float64)
        for hit in self.lexical.search(query, top_k=len(self.messages)):
            lexical[self.id_to_index[hit.id]] = hit.lexical_score
        person_match = np.array([constraints.person_mode != 'none' and row.sender == constraints.person
                                 for row in self.messages], dtype=bool)
        date_match = np.zeros(len(self.messages), dtype=bool)
        if constraints.start_date:
            date_match = np.array([
                constraints.start_date <= stamp.date().isoformat() <= constraints.end_date
                and (constraints.hour_range is None or constraints.hour_range[0] <= stamp.hour < constraints.hour_range[1])
                for stamp in self.local_times], dtype=bool)
        eligible = np.ones(len(self.messages), dtype=bool)
        if constraints.person_mode == 'filter':
            eligible &= person_match
        if constraints.start_date:
            eligible &= date_match
        return QuerySignals(constraints, semantic, contextual, lexical, person_match, date_match, eligible)

    def rank(self, signals, top_k=5, config=None):
        if type(top_k) is not int or top_k < 1:
            raise ValueError('top_k must be a positive integer')
        if signals is None:
            return []
        config = self.config if config is None else config
        weights = config.weights(signals.constraints.has_filter)
        bonuses = weights['person_bonus'] * signals.person_match + weights['date_bonus'] * signals.date_match
        scores = (weights['semantic'] * signals.semantic + weights['contextual'] * signals.contextual
                  + weights['lexical'] * signals.lexical + bonuses)
        candidates = np.flatnonzero(signals.eligible)
        ranked = sorted(candidates, key=lambda i: (-float(scores[i]), self.messages[i].id))[:top_k]
        details = {'profile': config.name, 'weights': weights,
                   'constraints': signals.constraints.to_dict(),
                   'eligible_message_count': int(signals.eligible.sum()),
                   'excluded_message_count': int((~signals.eligible).sum())}
        return [HybridResult(
            self.messages[i].id, self.messages[i].sender, self.messages[i].timestamp,
            self.messages[i].text, self.messages[i].text, float(scores[i]),
            float(signals.semantic[i]), float(signals.contextual[i]), float(signals.lexical[i]),
            bool(signals.person_match[i]), bool(signals.date_match[i]), float(bonuses[i]),
            self.contexts[i].context_text, self.contexts[i].context_message_ids,
            tuple({**asdict(row), 'is_current': row.id == self.messages[i].id} for row in self.contexts[i].messages),
            details) for i in ranked]

    def search(self, query, top_k=5):
        if type(top_k) is not int or top_k < 1:
            raise ValueError('top_k must be a positive integer')
        return self.rank(self.prepare(query), top_k)

    def configuration(self):
        return {
            'ranking': self.config.to_dict(),
            'routing': 'Hard author/date constraints shift context weight to the original message.',
            'normalization': 'Clamp embedding cosine to [0,1]; TF-IDF is already [0,1]; no per-query min/max rescaling.',
            'metadata': 'Explicit sender and chat-date filters; uncertain person mention gets a bonus; topic names do not.',
            'empty_filter_policy': 'Return [] without silently relaxing constraints.',
            'context_policy': 'Filter and credit the current message only; neighbors may have other authors/dates.',
            'reference_date': self.parser.reference_date.isoformat(), 'timezone': self.parser.timezone,
            'month_part_days_inclusive': MONTH_PARTS, 'day_part_hours_half_open': DAY_PARTS,
            'query_text_policy': 'Original raw query is used for all similarity channels.',
            'tie_break': 'message ID ascending for exactly equal scores',
            'candidate_policy': 'Score the entire corpus, then intersect hard constraints before top K.',
            'tuning': 'Four general profiles measured on the same 40 queries; see results/hybrid_tuning.json. These are development-set metrics.',
            'semantic': self.semantic.configuration(), 'contextual': self.contextual.configuration(),
            'lexical': self.lexical.configuration(),
        }
