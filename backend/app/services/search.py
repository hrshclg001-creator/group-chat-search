"""One corpus, context lookup and hybrid index for each application lifespan."""

from dataclasses import asdict
import json
import logging
from threading import Lock
from time import perf_counter

from ..query_understanding import QueryParser
from ..query_understanding.parser import DEFAULT_METADATA_PATH
from ..schemas import InterpretedQuery, SearchResponse, SearchResultResponse, StatsResponse
from ..search.corpus import load_corpus
from .conversation import ConversationContext


logger = logging.getLogger(__name__)


class SearchUnavailable(RuntimeError):
    pass


class SearchService:
    def __init__(self, messages, metadata, engine=None):
        self.context = ConversationContext(messages)
        self.engine = engine
        self.lock = Lock()
        participants = {item['name'] for item in metadata['participants']}
        if participants != {row.sender for row in self.context.messages}:
            raise ValueError('Corpus senders disagree with participant metadata')
        self.stats = StatsResponse(
            message_count=len(self.context.messages), participant_count=len(participants),
            date_range={'start': self.context.messages[0].timestamp, 'end': self.context.messages[-1].timestamp},
            reference_date=metadata['reference_date'], timezone=metadata['timezone'])

    @classmethod
    def from_disk(cls):
        # This factory is called only at startup, never from the request path.
        messages = load_corpus()
        with DEFAULT_METADATA_PATH.open(encoding='utf-8') as stream:
            metadata = json.load(stream)
        parser = QueryParser(metadata)
        service = cls(messages, metadata)
        try:
            from ..search.reranked import RerankedSearch
            service.engine = RerankedSearch(messages, parser=parser)
        except (OSError, ValueError):
            logger.exception('Local search index could not initialize; health and corpus stats remain available')
        return service

    @staticmethod
    def interpretation(constraints):
        parsed = constraints.parsed_query
        person_active = constraints.person_mode != 'none'
        return InterpretedQuery(
            raw_query=parsed['raw_query'], person=constraints.person,
            person_mode=constraints.person_mode, person_candidates=parsed['person_candidates'],
            start_date=constraints.start_date, end_date=constraints.end_date, hour_range=constraints.hour_range,
            intent=('person_' if person_active else '') + ('time_' if constraints.start_date else '') + 'semantic',
            reference_date=parsed['reference_date'], timezone=parsed['timezone'],
            warnings=parsed['warnings'], explanations=list(constraints.reasons), message_type=constraints.message_type)

    def search(self, query, top_k):
        if self.engine is None:
            raise SearchUnavailable(
                'Search index unavailable. Prepare the local model with '
                '`cd backend; python -m scripts.prepare_model` and `python -m scripts.prepare_reranker`, '
                'check server startup logs, and restart the backend.')
        started = perf_counter()
        # Synchronous FastAPI routes run in a thread pool. Serialize access to
        # the shared encoder; statistics and health do not acquire this lock.
        with self.lock:
            signals = self.engine.prepare(query)
            hits = self.engine.rank(signals, top_k=top_k)
        interpreted = self.interpretation(signals.constraints)
        results = []
        for rank, hit in enumerate(hits, 1):
            current, previous, following = self.context.around(hit.id)
            results.append(SearchResultResponse(
                matching_message=asdict(current), previous_messages=[asdict(row) for row in previous],
                next_messages=[asdict(row) for row in following], search_score=hit.hybrid_score,
                semantic_score=hit.semantic_score, contextual_score=hit.contextual_score,
                lexical_score=hit.lexical_score, reranker_score=hit.reranker_score,
                query_metadata=interpreted, rank=rank))
        return SearchResponse(query=query, interpreted_query=interpreted,
                              search_time_ms=round((perf_counter() - started) * 1000, 3), results=results)
