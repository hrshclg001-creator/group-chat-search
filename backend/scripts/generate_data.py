"""Generate an entirely synthetic corpus using only the Python standard library.

Run from backend: python -m scripts.generate_data
"""

import argparse
import hashlib
import json
import platform
import random
from collections import Counter
from datetime import datetime, time, timedelta
from pathlib import Path

from .conversation_content import SCENES, SLOTS, TASKS
from .chat_style import render_chat
from .corpus_config import (
    END_DATE, GENERATOR_VERSION, IST, PARTICIPANTS, REFERENCE_DATE, SEED,
    START_DATE, THREAD_IDS,
)
from .decision_threads import CONCLUSIONS, THREADS

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / 'data'


def message_type(text):
    for prefix, kind in [('[Image]', 'image'), ('[PDF]', 'pdf'),
                         ('[Voice message]', 'voice'), ('Forwarded:', 'forwarded')]:
        if text.startswith(prefix):
            return kind
    return 'url' if 'https://' in text else 'text'


def encode_messages(messages):
    """Canonical UTF-8 JSONL with LF line endings on every platform."""
    return ''.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n'
                   for row in messages).encode('utf-8')


def generate_messages(seed=SEED):
    rng = random.Random(seed)
    records = []
    last_used = {}

    def add(when, speaker, text, topic, episode_id, thread_id=None):
        participant = PARTICIPANTS[speaker]
        record = {
            'timestamp': when.isoformat(timespec='seconds'),
            'sender': participant['name'],
            'text': text,
            'message_type': message_type(text),
            'metadata': {'participant_id': participant['id'], 'topic': topic,
                         'episode_id': episode_id},
        }
        if thread_id:
            record['thread_id'] = thread_id
        records.append(record)
        return record

    add(datetime.combine(START_DATE, time(7, 5), IST), 1,
        'March aa gaya. Keeping this group for class stuff, chai plans and all our random nonsense 😅',
        'random', 'OPENING')

    day_count = (END_DATE - START_DATE).days + 1
    daily_counts = [2, 3, 4] * (day_count // 3) + [3] * (day_count % 3)
    rng.shuffle(daily_counts)
    for day_index in range(day_count):
        day = START_DATE + timedelta(days=day_index)
        # Vary activity by date while retaining 552 complete conversations.
        hours = {2: (8, 21), 3: (8, 13, 21), 4: (8, 12, 17, 21)}[daily_counts[day_index]]
        for slot, hour in enumerate(hours):
            eligible = [i for i, scene in enumerate(SCENES) if day.month in scene[1]]
            recent_free = [i for i in eligible if day_index - last_used.get(i, -100) > 7]
            if not recent_free:
                oldest = min(last_used.get(i, -100) for i in eligible)
                recent_free = [i for i in eligible if last_used.get(i, -100) == oldest]
            index = rng.choice(recent_free)
            last_used[index] = day_index
            topic, _, script = SCENES[index]
            roles = rng.sample(range(8), 4)
            episode_id = f'DAILY_{day:%Y%m%d}_{slot + 1}'
            values = {key: rng.choice(options) for key, options in SLOTS.items()}
            values.update({
                'task': rng.choice(TASKS[values['subject']]),
                'meet_time': rng.choice(['4:30 pm', '5 pm', '6:15 pm', '7 pm', '8:30 pm'])
                if hour < 21 else rng.choice(['9:30 pm', '9:45 pm', '10 pm']),
                'date_label': day.isoformat(),
                'due_date': (day + timedelta(days=rng.randint(2, 6))).isoformat(),
                'episode_slug': episode_id.lower(),
                'cash': rng.choice([40, 60, 80, 100, 120]),
                'file_size': rng.choice([12, 18, 24, 31, 42]),
                'room': rng.choice(['B-201', 'B-204', 'C-102', 'A-305', 'C-203']),
                'battery': rng.choice([2, 3, 5, 7, 9]),
            })
            when = datetime.combine(day, time(hour, rng.randint(0, 12)), IST)
            lines = script.splitlines()
            if len(lines) != 8:
                raise ValueError(f'Background scene {index} must contain eight messages')
            for line in lines:
                role, text = line.split('|', 1)
                speaker = roles[int(role)]
                rendered = render_chat(text.format(**values), speaker, rng)
                add(when, speaker, rendered, topic, episode_id)
                when += timedelta(seconds=rng.randint(25, 210))

    conclusions = {}
    for thread_id in THREAD_IDS:
        for episode_index, (day, clock, script) in enumerate(THREADS[thread_id]):
            when = datetime.fromisoformat(f'{day}T{clock}:00').replace(tzinfo=IST)
            lines = script.splitlines()
            if len(lines) != 12:
                raise ValueError(f'{thread_id} episode must contain twelve messages')
            for line_index, line in enumerate(lines):
                speaker, text = line.split('|', 1)
                record = add(when, int(speaker) - 1, text, 'decision_discussion',
                             f'{thread_id}_{episode_index + 1}', thread_id)
                if (episode_index, line_index) == CONCLUSIONS[thread_id]:
                    conclusions[thread_id] = record
                when += timedelta(seconds=rng.randint(120, 300))

    add(datetime.combine(END_DATE, time(23, 50), IST), 7,
        'August khatam. September reminders kal dekhte, ab so jao. gn 🌙',
        'random', 'CLOSING')
    # Stable sorting also resolves any coincident timestamps deterministically.
    records.sort(key=lambda row: row['timestamp'])
    messages = []
    for number, record in enumerate(records, 1):
        record['id'] = f'MSG_{number:06d}'
        messages.append({'id': record['id'], **{k: v for k, v in record.items() if k != 'id'}})
    return messages, {key: row['id'] for key, row in conclusions.items()}


def generate_corpus(seed=SEED):
    messages, conclusion_ids = generate_messages(seed)
    payload = encode_messages(messages)
    thread_details = {}
    for thread_id in THREAD_IDS:
        rows = [row for row in messages if row.get('thread_id') == thread_id]
        thread_details[thread_id] = {
            'message_count': len(rows),
            'first_message_id': rows[0]['id'],
            'last_message_id': rows[-1]['id'],
            'message_ids': [row['id'] for row in rows],
            'start': rows[0]['timestamp'],
            'end': rows[-1]['timestamp'],
            'episode_count': len({row['metadata']['episode_id'] for row in rows}),
            'conclusion_message_id': conclusion_ids[thread_id],
        }
    metadata = {
        'synthetic': True,
        'participants': PARTICIPANTS,
        'corpus_start': messages[0]['timestamp'],
        'corpus_end': messages[-1]['timestamp'],
        'reference_date': REFERENCE_DATE.isoformat(),
        'timezone': 'Asia/Kolkata',
        'message_count': len(messages),
        'decision_thread_ids': list(THREAD_IDS),
        'decision_threads': thread_details,
        'generation': {
            'seed': seed,
            'generator_version': GENERATOR_VERSION,
            'python_version': platform.python_version(),
            'dependencies': 'Python standard library only',
            'date_start': START_DATE.isoformat(),
            'date_end': END_DATE.isoformat(),
            'daily_episode_range': [2, 4],
            'background_episode_count': 552,
            'messages_per_daily_episode': 8,
            'background_scene_count': len(SCENES),
            'serialization': 'UTF-8, compact JSONL, LF, one trailing newline per record',
        },
        'sha256': hashlib.sha256(payload).hexdigest(),
        'message_type_counts': dict(sorted(Counter(row['message_type'] for row in messages).items())),
        'topic_counts': dict(sorted(Counter(row['metadata']['topic'] for row in messages).items())),
        'limitations': [
            'Entirely fictional people, institution, quotes, notices, events and transactions.',
            'Background vignettes are templated; repeated routines and short replies are intentional.',
            'Thread boundaries and conclusion IDs support corpus review, not retrieval ranking or evaluation labels.',
            'No evaluation queries, search results, or benchmark measurements are included.',
        ],
    }
    return messages, metadata


def write_corpus(output_dir=DEFAULT_OUTPUT, seed=SEED):
    from .validate_data import validate_corpus

    messages, metadata = generate_corpus(seed)
    validate_corpus(messages, metadata)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'messages.jsonl').write_bytes(encode_messages(messages))
    (output_dir / 'corpus_metadata.json').write_bytes(
        (json.dumps(metadata, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    metadata = write_corpus(args.output_dir)
    print(f"Generated {metadata['message_count']} synthetic messages in {args.output_dir}")
    print(f"SHA-256: {metadata['sha256']}")


if __name__ == '__main__':
    main()
