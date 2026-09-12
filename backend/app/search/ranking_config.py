"""All hybrid weights and routing thresholds, visible and versioned.

Four general profiles are compared by evaluation/tune_hybrid.py. No query IDs,
target IDs, category labels or benchmark text belong in this module.
"""

from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class RankingConfig:
    name: str
    contextual: float
    semantic: float
    lexical: float
    person_bonus: float = 0.05
    date_bonus: float = 0.05
    constrained_context_to_original: float = 0.10

    def __post_init__(self):
        values = (self.contextual, self.semantic, self.lexical, self.person_bonus, self.date_bonus)
        if any(not math.isfinite(value) or value < 0 for value in values):
            raise ValueError('Ranking weights must be finite and nonnegative')
        if not math.isclose(sum(values), 1.0):
            raise ValueError('Ranking weights and metadata bonuses must sum to one')
        if not 0 <= self.constrained_context_to_original <= self.contextual:
            raise ValueError('Constrained context transfer exceeds its available weight')

    def weights(self, constrained):
        transfer = self.constrained_context_to_original if constrained else 0.0
        return {'contextual': self.contextual - transfer,
                'semantic': self.semantic + transfer, 'lexical': self.lexical,
                'person_bonus': self.person_bonus, 'date_bonus': self.date_bonus}

    def to_dict(self):
        return asdict(self)


PROFILES = {
    'context_first': RankingConfig('context_first', 0.55, 0.20, 0.15),
    'balanced': RankingConfig('balanced', 0.35, 0.35, 0.20),
    'original_first': RankingConfig('original_first', 0.20, 0.55, 0.15),
    'anchor_first': RankingConfig('anchor_first', 0.10, 0.65, 0.15),
}
# Updated only after the documented aggregate comparison, never per query.
DEFAULT_PROFILE = 'balanced'
DEFAULT_CONFIG = PROFILES[DEFAULT_PROFILE]

# General date-refinement conventions (inclusive days, half-open hour ranges).
MONTH_PARTS = {'early': (1, 7), 'start': (1, 7), 'mid': (11, 20), 'late': (21, 31)}
DAY_PARTS = {'morning': (0, 12), 'afternoon': (12, 17), 'evening': (17, 21), 'night': (21, 24)}
