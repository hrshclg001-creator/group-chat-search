"""Versioned lexical-overlap audit; deliberately independent of retrieval."""

import json
import re
import unicodedata
from pathlib import Path

CONVENTION_PATH = Path(__file__).with_name('overlap_convention.json')
CONVENTION = json.loads(CONVENTION_PATH.read_text(encoding='utf-8'))
STOPWORDS = frozenset(CONVENTION['stopwords'])


def content_words(text):
    text = unicodedata.normalize('NFKC', text).casefold().replace('\u2019', "'")
    text = re.sub(r"\bcan't\b", 'can not', text)
    text = re.sub(r"\bwon't\b", 'will not', text)
    text = re.sub(r"n't\b", ' not', text)
    for suffix, expansion in [("'ll", ' will'), ("'re", ' are'), ("'ve", ' have'),
                              ("'m", ' am'), ("'d", ' would'), ("'s", '')]:
        text = re.sub(re.escape(suffix) + r'\b', expansion, text)
    return set(re.findall(r'[^\W_]+', text, flags=re.UNICODE)) - STOPWORDS


def overlap_details(query, target_text):
    query_words = content_words(query)
    target_words = content_words(target_text)
    shared = query_words & target_words
    return {
        'query_content_words': sorted(query_words),
        'target_content_words': sorted(target_words),
        'shared_content_words': sorted(shared),
        'zero_word_overlap': bool(query_words and target_words and not shared),
    }
