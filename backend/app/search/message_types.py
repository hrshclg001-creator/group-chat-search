"""Conservative requests for actual message types, not mentions of them."""

import re

from ..query_understanding.parser import normalize


def requested_message_type(query):
    text = normalize(query).replace('\u2019', "'")
    # Negation, alternatives and asking about a mention are deliberately not
    # interpreted as a positive type constraint.
    if re.search(r"\b(?:not|never|without|except|or|versus|mention\w*|discuss\w*)\b|n't\b", text):
        return None
    request = r'^(?:find|show|locate|get|which|what|where\s+is)\s+(?:(?:me|us|the|a|an|first|last|latest|earliest|all)\s+)*'
    kinds = {
        'forwarded': r'forwarded\s+(?:messages?|notices?|warnings?|updates?)\b',
        'pdf': r'pdf\b',
        'image': r'(?:image|photo|picture)\b',
        'voice': r'(?:voice\s+(?:message|note)|audio\s+message)\b',
        'url': r'(?:url|link)\b',
    }
    selected = {kind for kind, noun in kinds.items() if re.search(request + noun, text)}
    # A question asking what somebody forwarded requests the forwarded item,
    # whereas "what did somebody say about forwarding" does not.
    if re.search(r'\b(?:did|had)\s+\w+(?:\s+\w+)?\s+forward\b', text):
        selected.add('forwarded')
    return next(iter(selected)) if len(selected) == 1 else None
