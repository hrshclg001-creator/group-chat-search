"""Versioned, fictional corpus configuration; no private chat inputs."""

from datetime import date, timedelta, timezone

SEED = 20260901
GENERATOR_VERSION = '1.0.0'
START_DATE = date(2026, 3, 1)
END_DATE = date(2026, 8, 31)
REFERENCE_DATE = date(2026, 9, 1)
IST = timezone(timedelta(hours=5, minutes=30))
PARTICIPANTS = [
    {'id': 'P01', 'name': 'Aarav Sharma', 'profile': 'Indore day scholar; enjoys coding and cricket'},
    {'id': 'P02', 'name': 'Ananya Verma', 'profile': 'Hosteller; organises deadlines and likes photography'},
    {'id': 'P03', 'name': 'Rohan Mehta', 'profile': 'Hosteller; movie enthusiast and enthusiastic trip planner'},
    {'id': 'P04', 'name': 'Ishita Patel', 'profile': 'Day scholar; design volunteer and careful with budgets'},
    {'id': 'P05', 'name': 'Kabir Khan', 'profile': 'Hosteller; tinkers with hardware and forgets chargers'},
    {'id': 'P06', 'name': 'Sneha Iyer', 'profile': 'Hosteller; likes backend development and filter coffee'},
    {'id': 'P07', 'name': 'Aditya Joshi', 'profile': 'Day scholar; cycling, badminton and terrible puns'},
    {'id': 'P08', 'name': 'Meera Nair', 'profile': 'Hosteller; enjoys books, music and event logistics'},
]
MESSAGE_TYPES = {'text', 'forwarded', 'url', 'image', 'pdf', 'voice'}
THREAD_IDS = ('TRIP_MANALI', 'HACKATHON_STACK', 'BIRTHDAY_EVENT')
