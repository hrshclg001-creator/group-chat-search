"""Display context independent of the smaller embedding window."""

from datetime import datetime


class ConversationContext:
    WINDOW_PER_SIDE = 3
    MAX_DISTANCE_SECONDS = 1800

    def __init__(self, messages):
        self.messages = tuple(sorted(messages, key=lambda row: (datetime.fromisoformat(row.timestamp), row.id)))
        self.positions = {row.id: index for index, row in enumerate(self.messages)}
        if not self.messages or len(self.positions) != len(self.messages):
            raise ValueError('Conversation context requires nonempty messages with unique IDs')
        self.timestamps = tuple(datetime.fromisoformat(row.timestamp) for row in self.messages)
        if any(stamp.utcoffset() is None for stamp in self.timestamps):
            raise ValueError('Conversation timestamps must be timezone-aware')

    def around(self, message_id):
        index = self.positions[message_id]
        stamp = self.timestamps[index]

        def nearby(indices):
            return tuple(self.messages[i] for i in indices
                         if abs((self.timestamps[i] - stamp).total_seconds()) <= self.MAX_DISTANCE_SECONDS)

        previous = nearby(range(max(0, index - self.WINDOW_PER_SIDE), index))
        following = nearby(range(index + 1, min(len(self.messages), index + self.WINDOW_PER_SIDE + 1)))
        return self.messages[index], previous, following
