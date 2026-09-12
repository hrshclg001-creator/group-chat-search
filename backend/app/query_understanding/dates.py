"""Small explicit date grammar using a supplied reference date, never a clock."""

import calendar
from datetime import date, timedelta
import re


ENGLISH_MONTHS = ('january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december')
MONTHS = {alias: number for number, name in enumerate(ENGLISH_MONTHS, 1)
          for alias in (name, name[:3])}
MONTHS['sept'] = 9
MONTH = '(?:' + '|'.join(sorted(MONTHS, key=len, reverse=True)) + ')'
DAY = r'\d{1,2}(?:st|nd|rd|th)?'
YEAR = r'\d{4}'
ISO = r'\d{4}-\d{2}-\d{2}'
NAMED = rf'(?:{DAY}\s+{MONTH}|{MONTH}\s+{DAY})(?:,?\s+{YEAR})?'
ENDPOINT = rf'(?:{ISO}|{NAMED}|{MONTH}(?:\s+{YEAR})?)'
CONNECTOR = r'(?:to|through|until|and|se|[-–—])'
RANGE = re.compile(rf'(?<!\w)({ENDPOINT})\s*{CONNECTOR}\s*({ENDPOINT})(?!\w)')
SHARED_MONTH_RANGE = re.compile(
    rf'(?<!\w)({DAY})\s*{CONNECTOR}\s*({DAY})\s+({MONTH})(?:,?\s+({YEAR}))?(?!\w)')
MONTH_FIRST_RANGE = re.compile(
    rf'(?<!\w)({MONTH})\s+({DAY})\s*{CONNECTOR}\s*({DAY})(?:,?\s+({YEAR}))?(?!\w)')
SINGLE = re.compile(rf'(?<!\w)({ENDPOINT})(?!\w)')


def month_bounds(year, month):
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


def endpoint(value, default_year):
    """Return inclusive bounds and whether the year was explicit."""
    if re.fullmatch(ISO, value):
        parsed = date.fromisoformat(value)
        return parsed, parsed, True
    parts = value.replace(',', '').split()
    has_year = bool(re.fullmatch(YEAR, parts[-1]))
    year = int(parts.pop()) if has_year else default_year
    month_token = next(part for part in parts if part in MONTHS)
    month = MONTHS[month_token]
    days = [part for part in parts if part != month_token]
    if not days:
        return (*month_bounds(year, month), has_year)
    day = int(re.sub(r'(st|nd|rd|th)$', '', days[0]))
    parsed = date(year, month, day)
    return parsed, parsed, has_year


def parse_dates(text, reference_date):
    """Return (start, end, warnings), with ISO strings or None.

    Multiple compatible constraints intersect. Disjoint alternatives, reversed
    ranges and invalid dates stay unresolved, rather than silently picking one.
    """
    spans = []
    intervals = []
    warnings = []

    def available(match):
        return not any(match.start() < end and match.end() > start for start, end in spans)

    def add(match, resolver):
        if not available(match):
            return
        spans.append(match.span())
        try:
            start, end = resolver()
            if start > end:
                raise ValueError('range starts after it ends')
            intervals.append((start, end))
        except ValueError:
            warnings.append(f'Invalid or reversed date expression: {match.group(0)}')

    def resolve_range(match):
        left, right = match.groups()
        start, _, left_year = endpoint(left, reference_date.year)
        _, end, right_year = endpoint(right, reference_date.year)
        # One explicit year applies to both ends. Cross-year ranges require
        # explicit years at both ends; no invisible year rollover is inferred.
        if left_year and not right_year:
            _, end, _ = endpoint(right, start.year)
        elif right_year and not left_year:
            start, _, _ = endpoint(left, end.year)
        return start, end

    def range_is_explicit(match):
        # "July and August" is not silently expanded into one interval;
        # the "and" connector is supported in "between X and Y" only.
        return not re.search(r'\band\b', match.group(0)) or bool(
            re.search(r'\bbetween\s+$', text[:match.start()]))

    for match in RANGE.finditer(text):
        if range_is_explicit(match):
            add(match, lambda match=match: resolve_range(match))
    for pattern, month_first in ((SHARED_MONTH_RANGE, False), (MONTH_FIRST_RANGE, True)):
        for match in pattern.finditer(text):
            if not range_is_explicit(match):
                continue
            def resolve_shared(match=match, month_first=month_first):
                first, second, third, year = match.groups()
                month, first_day, last_day = (first, second, third) if month_first else (third, first, second)
                year = int(year) if year else reference_date.year
                return endpoint(f'{first_day} {month} {year}', year)[0], endpoint(f'{last_day} {month} {year}', year)[1]
            add(match, resolve_shared)

    previous_month_end = reference_date.replace(day=1) - timedelta(days=1)
    current_week_start = reference_date - timedelta(days=reference_date.weekday())
    relative = (
        (r'today|aaj', (reference_date, reference_date)),
        (r'yesterday|beete\s+kal|beetey\s+kal', (reference_date - timedelta(days=1),) * 2),
        (r'last\s+week|pich(?:le|hle)\s+hafte',
         (current_week_start - timedelta(days=7), current_week_start - timedelta(days=1))),
        (r'last\s+month|pich(?:le|hle)\s+mahine', month_bounds(previous_month_end.year, previous_month_end.month)),
        (r'this\s+month|is\s+mahine', month_bounds(reference_date.year, reference_date.month)),
    )
    for expression, interval in relative:
        for match in re.finditer(rf'(?<!\w)(?:{expression})(?!\w)', text):
            add(match, lambda interval=interval: interval)

    for match in SINGLE.finditer(text):
        # Auxiliary "may" is not a month without a date cue. Other month
        # names/abbreviations are recognized as whole words.
        if match.group(0) == 'may' and text != 'may' and not (
            re.search(r'\b(?:in|during|of|from|since|for|about)\s+$', text[:match.start()]) or
            re.match(r'\s+(?:messages|mein|ki|ka|ke)\b', text[match.end():])
        ):
            continue
        add(match, lambda match=match: endpoint(match.group(0), reference_date.year)[:2])

    # Numeric slash dates have conflicting regional interpretations. Bare
    # "kal" can mean yesterday or tomorrow; do not silently resolve either.
    for pattern, warning in (
        (r'\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b', 'Ambiguous numeric date; use YYYY-MM-DD or a month name.'),
        (r'\bkal\b', 'Ambiguous "kal"; use yesterday, today, or an explicit date.'),
    ):
        if any(available(match) for match in re.finditer(pattern, text)):
            warnings.append(warning)
    if warnings:
        return None, None, tuple(warnings)
    if not intervals:
        return None, None, ()
    start = max(interval[0] for interval in intervals)
    end = min(interval[1] for interval in intervals)
    if start > end:
        return None, None, ('Conflicting time constraints; no single date interval was selected.',)
    return start.isoformat(), end.isoformat(), ()
