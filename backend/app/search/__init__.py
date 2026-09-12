"""Local retrieval over message text; no evaluation-label dependencies."""

from .corpus import Message, load_corpus
from .lexical import LexicalSearch, SearchResult

__all__ = ['Message', 'load_corpus', 'LexicalSearch', 'SearchResult']
