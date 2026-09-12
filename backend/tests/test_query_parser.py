"""Query grammar tests use metadata and fixtures, never evaluation labels."""

from datetime import date
import json

import pytest

from app.query_understanding import QueryParser
from app.query_understanding import dates, parser as parser_module


@pytest.fixture
def parser():
    return QueryParser.from_metadata()


def metadata(reference='2026-09-01', names=('Priya Sharma', 'Rahul Verma', 'Aman Khan')):
    return {'reference_date': reference, 'timezone': 'Asia/Kolkata',
            'participants': [{'name': name} for name in names]}


@pytest.mark.parametrize('query,expected', [
    ('what did Priya say about the budget?', 'Priya Sharma'),
    ('Rahul ne kya bola about exams?', 'Rahul Verma'),
    ('message from Aman about the assignment', 'Aman Khan'),
    ('PRIYA SHARMA\'s notes', 'Priya Sharma'),
    ('Verma ne kya bola?', 'Rahul Verma'),
    ('Aman, please send it', 'Aman Khan'),
])
def test_english_and_hinglish_name_patterns(query, expected):
    result = QueryParser(metadata()).parse(query)
    assert result.person == expected
    assert result.intent == 'person_semantic'
    assert result.raw_query == query
    assert result.warnings == ()


def test_real_participants_come_from_metadata(parser):
    assert len(parser.names) == 8
    for name in parser.names:
        assert parser.parse(f'What did {name.split()[0]} say?').person == name
    assert parser.parse('What did Priya say?').person is None
    assert parser.parse('Rohanathan sent an update').person is None
    assert parser.parse('Sneha_Iyer update').person is None


def test_multiple_people_are_not_arbitrarily_reduced(parser):
    result = parser.parse('What did Aarav say to Meera?')
    assert result.person is None
    assert result.person_candidates == ('Aarav Sharma', 'Meera Nair')
    assert result.warnings


def test_shared_alias_is_ambiguous_but_full_name_resolves():
    parser = QueryParser(metadata(names=('Priya Sharma', 'Priya Patel')))
    assert parser.parse('Priya ne kya bola?').person is None
    assert parser.parse('Priya ne kya bola?').warnings
    assert parser.parse('Priya Patel ne kya bola?').person == 'Priya Patel'


@pytest.mark.parametrize('query,start,end', [
    ('today', '2026-09-01', '2026-09-01'),
    ('What happened yesterday?', '2026-08-31', '2026-08-31'),
    ('last week ki updates', '2026-08-24', '2026-08-30'),
    ('last month', '2026-08-01', '2026-08-31'),
    ('this month', '2026-09-01', '2026-09-30'),
    ('aaj kya hua?', '2026-09-01', '2026-09-01'),
    ('beete kal kya bola?', '2026-08-31', '2026-08-31'),
    ('pichle hafte kya decide hua?', '2026-08-24', '2026-08-30'),
    ('pichhle mahine budget kitna tha?', '2026-08-01', '2026-08-31'),
    ('is mahine ki baat', '2026-09-01', '2026-09-30'),
    ('in August', '2026-08-01', '2026-08-31'),
    ('during May', '2026-05-01', '2026-05-31'),
    ('May', '2026-05-01', '2026-05-31'),
    ('May mein kya bola?', '2026-05-01', '2026-05-31'),
    ('December messages', '2026-12-01', '2026-12-31'),
    ('Feb 2024 messages', '2024-02-01', '2024-02-29'),
    ('on 2026-08-15', '2026-08-15', '2026-08-15'),
    ('on 15th August 2026', '2026-08-15', '2026-08-15'),
    ('on August 15, 2026', '2026-08-15', '2026-08-15'),
    ('from 2026-03-01 to 2026-08-31', '2026-03-01', '2026-08-31'),
    ('between 1 March and 5 April 2026', '2026-03-01', '2026-04-05'),
    ('from August 1 to August 15', '2026-08-01', '2026-08-15'),
    ('1-15 August 2026 ki baat', '2026-08-01', '2026-08-15'),
    ('August 1-15, 2026', '2026-08-01', '2026-08-15'),
    ('1 Aug se 15 Aug tak', '2026-08-01', '2026-08-15'),
    ('March through August', '2026-03-01', '2026-08-31'),
    ('Dec 30 2025 to Jan 2 2026', '2025-12-30', '2026-01-02'),
    ('March 2024 through April', '2024-03-01', '2024-04-30'),
    ('last month on August 15', '2026-08-15', '2026-08-15'),
])
def test_date_grammar(parser, query, start, end):
    result = parser.parse(query)
    assert (result.start_date, result.end_date) == (start, end)
    assert result.intent == 'time_semantic'
    assert result.reference_date == '2026-09-01'
    assert result.timezone == 'Asia/Kolkata'
    assert result.warnings == ()


@pytest.mark.parametrize('query', [
    'What happened kal?', 'on 03/04/2026', 'last month or this month',
    'from 2026-08-31 to 2026-03-01', '31 February 2026',
    '2026-02-30', 'Dec 30 to Jan 2',
    'in July and August',
])
def test_ambiguous_invalid_and_reversed_dates_are_visible(parser, query):
    result = parser.parse(query)
    assert result.start_date is None and result.end_date is None
    assert result.warnings


@pytest.mark.parametrize('query', ['', '   ', 'may I see the budget?', 'we may go',
                                    'maybe later', 'aajkal kya chal raha hai?', 'Someday soon'])
def test_plain_queries_do_not_acquire_constraints(parser, query):
    result = parser.parse(query)
    assert result.intent == 'semantic'
    assert result.person is result.start_date is result.end_date is None
    assert result.raw_query == query
    assert result.warnings == ()


def test_combined_query_serializes(parser):
    result = parser.parse('Ishita ne last month budget pe kya bola?').to_dict()
    assert result == {
        'raw_query': 'Ishita ne last month budget pe kya bola?',
        'person': 'Ishita Patel', 'start_date': '2026-08-01', 'end_date': '2026-08-31',
        'intent': 'person_time_semantic', 'reference_date': '2026-09-01',
        'timezone': 'Asia/Kolkata', 'person_candidates': ['Ishita Patel'], 'warnings': [],
    }
    assert json.loads(json.dumps(result)) == result


@pytest.mark.parametrize('reference,phrase,start,end', [
    ('2026-01-01', 'last month', '2025-12-01', '2025-12-31'),
    ('2026-01-01', 'last week', '2025-12-22', '2025-12-28'),
    ('2026-09-06', 'last week', '2026-08-24', '2026-08-30'),
    ('2026-09-07', 'last week', '2026-08-31', '2026-09-06'),
    ('2024-03-01', 'yesterday', '2024-02-29', '2024-02-29'),
    ('2024-03-01', 'last month', '2024-02-01', '2024-02-29'),
])
def test_reference_drives_year_week_and_leap_boundaries(reference, phrase, start, end):
    result = QueryParser(metadata(reference)).parse(phrase)
    assert (result.start_date, result.end_date) == (start, end)


def test_no_real_clock_is_consulted(monkeypatch):
    class NoClockDate(date):
        @classmethod
        def today(cls):
            raise AssertionError('Query parsing must not consult the wall clock')
    monkeypatch.setattr(parser_module, 'date', NoClockDate)
    monkeypatch.setattr(dates, 'date', NoClockDate)
    parser = QueryParser.from_metadata()
    assert parser.parse('today').start_date == '2026-09-01'
    assert parser.parse('last week').end_date == '2026-08-30'


@pytest.mark.parametrize('invalid', [
    {}, {'reference_date': None}, {'reference_date': '2026-02-30'},
    {'reference_date': '2026-09-01T00:00:00'}, {'timezone': None},
    {'participants': []}, {'participants': [{'name': ''}]},
    {'participants': [{'name': 'Priya'}, {'name': 'priya'}]},
])
def test_invalid_metadata_fails_without_clock_fallback(invalid):
    data = metadata()
    if not invalid:
        data.pop('reference_date')
    else:
        data.update(invalid)
    with pytest.raises(ValueError):
        QueryParser(data)


def test_nonstring_query_rejected(parser):
    with pytest.raises(TypeError):
        parser.parse(None)


def test_custom_metadata_file(tmp_path):
    path = tmp_path / 'metadata.json'
    path.write_text(json.dumps(metadata('2025-01-02')), encoding='utf-8')
    parsed = QueryParser.from_metadata(path).parse('Aman ne yesterday kya bola?')
    assert parsed.person == 'Aman Khan'
    assert parsed.start_date == parsed.end_date == '2025-01-01'
