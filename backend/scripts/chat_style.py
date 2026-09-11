"""Small meaning-preserving wording choices for recurring casual conversations.

These variations affect only background chat, never the authored decisions.
One-word replies and media/forward prefixes are preserved.
"""

import re

PHRASINGS = {
    'anyone': ['anyone', 'koi', 'anybody'],
    'please': ['please', 'pls', 'plz'],
    'thanks': ['thanks', 'thank you', 'thnks', 'shukriya'],
    'okay': ['okay', 'okayyy', 'theek hai', 'alright'],
    'actually': ['actually', 'honestly', 'tbh'],
    'tomorrow': ['tomorrow', 'kal'],
    'yesterday': ['yesterday', 'kal'],
    'today': ['today', 'aaj'],
    'tonight': ['tonight', 'aaj raat'],
    'good': ['good', 'nice', 'acha'],
    'small': ['small', 'little', 'tiny'],
    'still': ['still', 'abhi bhi'],
    'maybe': ['maybe', 'shayad'],
    'really': ['really', 'seriously'],
    'again': ['again', 'phir se'],
    'sorry': ['sorry', 'sorryy', 'sry'],
    'I have': ['I have', 'I have', "I've got"],
    "don't": ["don't", 'do not', 'dont'],
    "can't": ["can't", 'cannot', 'cant'],
    'not yet': ['not yet', 'abhi nahi'],
    'no rush': ['no rush', 'aaram se', 'take your time'],
    'let me': ['let me', 'lemme'],
    'a little': ['a little', 'thoda'],
    'five minutes': ['five minutes', '5 mins', 'five mins'],
    'ten minutes': ['ten minutes', '10 mins', 'ten mins'],
    'half an hour': ['half an hour', '30 mins'],
}


def render_chat(text, speaker, rng):
    if len(text.split()) <= 1 or text.startswith(('https://', '[', 'Forwarded:')):
        return text
    for phrase, choices in PHRASINGS.items():
        pattern = r'\b' + re.escape(phrase) + r'\b'
        if re.search(pattern, text, flags=re.IGNORECASE) and rng.random() < 0.55:
            text = re.sub(pattern, lambda match: rng.choice(choices), text,
                          count=1, flags=re.IGNORECASE)
    # Some participants type mostly in lowercase; others keep normal sentences.
    if speaker in (0, 2, 4, 6) and rng.random() < 0.6:
        text = text[:1].lower() + text[1:]
    if rng.random() < 0.18:
        text = text.replace('?', '??').replace('!', '!!')
    if rng.random() < 0.12 and not any(mark in text for mark in ('😂', '😭', '😅')):
        text += rng.choice([' 😅', ' 🙃', ' lol', ' yaar'])
    return text
