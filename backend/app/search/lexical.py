"""Two-channel TF-IDF baseline, configured before the first benchmark.

Only original message text is vectorized. No labels, thread annotations,
sender/date boosts, synonyms, embeddings or query-specific rules are used.
"""

from dataclasses import asdict, dataclass
from typing import Iterable, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .corpus import Message, load_corpus


@dataclass(frozen=True)
class SearchResult:
    id: str
    sender: str
    timestamp: str
    text: str
    lexical_score: float

    def to_dict(self):
        return asdict(self)


class LexicalSearch:
    """Fit on the corpus once, then return up to K positive-scoring messages."""

    WORD_WEIGHT = 0.7
    CHARACTER_WEIGHT = 0.3

    def __init__(self, messages: Iterable[Message]):
        # Stable input order and ID tie-breaking also make rebuilds reproducible.
        self.messages = tuple(sorted(messages, key=lambda message: message.id))
        if not self.messages:
            raise ValueError('Corpus is empty')
        if len({message.id for message in self.messages}) != len(self.messages):
            raise ValueError('Duplicate message IDs')
        if any(not isinstance(message.text, str) or not message.text.strip() for message in self.messages):
            raise ValueError('Message text must be nonempty')
        common = dict(lowercase=True, strip_accents='unicode', norm='l2',
                      use_idf=True, smooth_idf=True, sublinear_tf=True, dtype=np.float64)
        self.word_vectorizer = TfidfVectorizer(
            analyzer='word', ngram_range=(1, 2), token_pattern=r'(?u)\b\w+\b', **common)
        self.char_vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), **common)
        texts = [message.text for message in self.messages]
        self.word_matrix = self._fit_channel(self.word_vectorizer, texts)
        self.char_matrix = self._fit_channel(self.char_vectorizer, texts)

    @staticmethod
    def _fit_channel(vectorizer, texts):
        try:
            return vectorizer.fit_transform(texts)
        except ValueError as exc:
            # An all-emoji corpus can have no word vocabulary; the other channel
            # still works. Do not hide unrelated fitting failures.
            if 'empty vocabulary' not in str(exc):
                raise
            return None

    @classmethod
    def from_jsonl(cls, path=None):
        return cls(load_corpus() if path is None else load_corpus(path))

    def configuration(self):
        return {
            'indexed_fields': ['text'],
            'word': {'analyzer': 'word', 'ngram_range': [1, 2],
                     'token_pattern': r'(?u)\b\w+\b', 'weight': self.WORD_WEIGHT},
            'character': {'analyzer': 'char_wb', 'ngram_range': [3, 5],
                          'weight': self.CHARACTER_WEIGHT},
            'lowercase': True, 'strip_accents': 'unicode', 'stop_words': None,
            'norm': 'l2', 'use_idf': True, 'smooth_idf': True, 'sublinear_tf': True,
            'dtype': 'float64', 'min_df': 1, 'max_df': 1.0, 'max_features': None,
            'score': '0.7 * word_cosine + 0.3 * character_cosine',
            'tie_break': 'message ID ascending for exactly equal scores',
            'zero_score_policy': 'omit zero-score messages; empty/OOV query returns []',
            'empty_channel_policy': 'zero contribution; weights are not renormalized',
            'tuning': 'Fixed defaults chosen before scoring; no evaluation-driven tuning',
            'word_vocabulary_size': 0 if self.word_matrix is None else self.word_matrix.shape[1],
            'character_vocabulary_size': 0 if self.char_matrix is None else self.char_matrix.shape[1],
        }

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not isinstance(query, str):
            raise TypeError('query must be a string')
        if type(top_k) is not int or top_k < 1:
            raise ValueError('top_k must be a positive integer')
        if not query.strip():
            return []
        scores = np.zeros(len(self.messages), dtype=np.float64)
        for vectorizer, matrix, weight in (
            (self.word_vectorizer, self.word_matrix, self.WORD_WEIGHT),
            (self.char_vectorizer, self.char_matrix, self.CHARACTER_WEIGHT),
        ):
            if matrix is not None:
                query_vector = vectorizer.transform([query])
                # L2-normalized sparse vectors: dot product equals cosine.
                scores += weight * (matrix @ query_vector.T).toarray().ravel()
        candidates = np.flatnonzero(scores > 0)
        ranked = sorted(candidates, key=lambda index: (-float(scores[index]), self.messages[index].id))
        results = []
        for index in ranked[:top_k]:
            message = self.messages[index]
            results.append(SearchResult(message.id, message.sender, message.timestamp,
                                        message.text, float(scores[index])))
        return results
