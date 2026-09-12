"""Cosine retrieval with either original-only or bounded contextual embeddings."""

from dataclasses import asdict, dataclass
import hashlib

import numpy as np

from .context import build_contexts, fit_context_to_budget
from .embedding import LocalEncoder, cached_embeddings, normalize_vectors
from .model_config import EMBEDDING_CACHE


@dataclass(frozen=True)
class SemanticResult:
    id: str
    sender: str
    timestamp: str
    text: str
    original_text: str
    semantic_score: float
    context_text: str
    context_message_ids: tuple
    context_messages: tuple
    embedding_text: str
    truncated_message_ids: tuple

    def to_dict(self):
        return asdict(self)


class SemanticSearch:
    def __init__(self, messages, contextual=False, encoder=None, cache_dir=EMBEDDING_CACHE):
        self.contextual = contextual
        self.encoder = encoder if encoder is not None else LocalEncoder()
        self.contexts = build_contexts(messages, window_size=2 if contextual else 0)
        self.embedding_texts = []
        self.truncations = []
        for record in self.contexts:
            if contextual:
                text, truncated = fit_context_to_budget(record, self.encoder.tokenizer,
                                                        self.encoder.max_sequence_length)
            else:
                text = record.original_text
                limit = self.encoder.max_sequence_length - self.encoder.tokenizer.num_special_tokens_to_add(pair=False)
                ids = self.encoder.tokenizer.encode(text, add_special_tokens=False)
                truncated = [record.current.id] if len(ids) > limit else []
                if truncated:
                    text = self.encoder.tokenizer.decode(ids[:limit], skip_special_tokens=True)
            self.embedding_texts.append(text)
            self.truncations.append(tuple(truncated))
        if cache_dir is None:
            self.matrix = normalize_vectors(self.encoder.encode(self.embedding_texts))
            self.cache_key = None
        else:
            self.matrix, self.cache_key = cached_embeddings(self.encoder, self.embedding_texts, cache_dir)

    def configuration(self):
        return {
            'indexed_fields': ['context_text' if self.contextual else 'original_text'],
            'representation': 'Previous/Current/Following message markers' if self.contextual else 'original text only',
            'window_per_side': 2 if self.contextual else 0,
            'max_neighbor_distance_seconds': 1800,
            'context_message_ids_include_current': True,
            'context_order': 'timestamp then message ID; no thread/episode labels used',
            'token_budget_policy': 'Trim longest neighbors first, then current only if it alone exceeds budget',
            'records_with_truncated_embedding_input': sum(bool(ids) for ids in self.truncations),
            'current_messages_truncated_for_embedding': sum(record.current.id in ids for record, ids in zip(self.contexts, self.truncations)),
            'original_text_policy': 'Always preserve and return exact current message text',
            'score': 'NumPy cosine of normalized query and document embeddings',
            'tie_break': 'message ID ascending for exactly equal scores',
            'zero_score_policy': 'Return top K cosine matches; blank query returns []',
            'model': self.encoder.settings,
            'embedding_cache_key': self.cache_key,
            'embedding_matrix_sha256': hashlib.sha256(self.matrix.tobytes()).hexdigest(),
            'tuning': 'One fixed contextual configuration, selected before scoring; no label-based tuning',
        }

    def search(self, query, top_k=5):
        if not isinstance(query, str):
            raise TypeError('query must be a string')
        if type(top_k) is not int or top_k < 1:
            raise ValueError('top_k must be a positive integer')
        if not query.strip():
            return []
        query_vector = normalize_vectors(self.encoder.encode([query]))[0]
        scores = np.clip(self.matrix @ query_vector, -1.0, 1.0)
        ranked = sorted(range(len(self.contexts)),
                        key=lambda i: (-float(scores[i]), self.contexts[i].current.id))[:top_k]
        results = []
        for index in ranked:
            record = self.contexts[index]
            current = record.current
            results.append(SemanticResult(
                current.id, current.sender, current.timestamp, current.text, current.text,
                float(scores[index]), record.context_text, record.context_message_ids,
                tuple({**asdict(row), 'is_current': row.id == current.id} for row in record.messages),
                self.embedding_texts[index], self.truncations[index]))
        return results
