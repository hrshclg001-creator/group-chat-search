"""Multilingual pairwise relevance over bounded, metadata-eligible candidates."""

from dataclasses import replace
import hashlib
import json

import numpy as np

from .hybrid import HybridSearch
from .model_config import CPU_THREADS
from . import reranker_config as settings


def verify_manifest(directory):
    manifest = json.loads((directory / 'download_manifest.json').read_text(encoding='utf-8'))
    if (not isinstance(manifest, dict) or manifest.get('model_id') != settings.MODEL_ID
            or manifest.get('revision') != settings.MODEL_REVISION
            or not isinstance(manifest.get('sha256'), dict)
            or set(manifest['sha256']) != set(settings.MODEL_FILES)):
        raise ValueError('Invalid reranker manifest; restore a clean cache and run scripts.prepare_reranker')
    for name in settings.MODEL_FILES:
        digest = hashlib.sha256()
        with (directory / name).open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        if digest.hexdigest() != manifest['sha256'][name]:
            raise ValueError(f'Reranker integrity check failed: {name}')
        if name == 'model.safetensors' and digest.hexdigest() != settings.WEIGHTS_SHA256:
            raise ValueError('Reranker weights differ from the pinned upstream SHA-256')
    return manifest


class LocalReranker:
    def __init__(self):
        try:
            manifest = verify_manifest(settings.MODEL_DIRECTORY)
        except FileNotFoundError as exc:
            raise FileNotFoundError('Prepare the reranker: cd backend; python -m scripts.prepare_reranker') from exc
        import torch
        from sentence_transformers import CrossEncoder

        torch.set_num_threads(CPU_THREADS)
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True)
        self.model = CrossEncoder(str(settings.MODEL_DIRECTORY), device='cpu',
                                  max_length=settings.MAX_SEQUENCE_LENGTH, local_files_only=True,
                                  trust_remote_code=False, default_activation_function=torch.nn.Sigmoid())
        self.settings = {'model_id': settings.MODEL_ID, 'revision': settings.MODEL_REVISION,
                         'model_file_sha256': manifest['sha256'], 'device': 'cpu',
                         'cpu_threads': CPU_THREADS,
                         'batch_size': settings.BATCH_SIZE, 'max_length': settings.MAX_SEQUENCE_LENGTH,
                         'activation': 'sigmoid; relevance score is not calibrated accuracy'}

    def score(self, query, messages):
        pairs = [(query, f'{row.text}\nSender: {row.sender}. Sent: {row.timestamp[:10]}.')
                 for row in messages]
        return self.model.predict(pairs, batch_size=settings.BATCH_SIZE,
                                  show_progress_bar=False, convert_to_numpy=True)


class RerankedSearch(HybridSearch):
    def __init__(self, messages, *, reranker=None, **kwargs):
        super().__init__(messages, **kwargs)
        self.reranker = reranker if reranker is not None else LocalReranker()
        self.last_candidate_ids = ()

    def rank(self, signals, top_k=5, config=None):
        first = super().rank(signals, top_k=len(self.messages), config=config)
        if type(top_k) is not int or top_k < 1:
            raise ValueError('top_k must be a positive integer')
        if not first:
            self.last_candidate_ids = ()
            return []
        eligible = np.flatnonzero(signals.eligible)
        width = max(top_k, settings.CANDIDATES_PER_SIGNAL)
        selected = {hit.id for hit in first[:width]}
        for scores in (signals.semantic, signals.contextual, signals.lexical):
            indices = sorted(eligible, key=lambda i: (-float(scores[i]), self.messages[i].id))[:width]
            selected.update(self.messages[i].id for i in indices if scores[i] > 0)
        candidates = [hit for hit in first if hit.id in selected]
        self.last_candidate_ids = tuple(hit.id for hit in candidates)
        rows = [self.messages[self.id_to_index[hit.id]] for hit in candidates]
        scores = np.asarray(self.reranker.score(signals.constraints.parsed_query['raw_query'], rows)).reshape(-1)
        if len(scores) != len(rows) or not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
            raise ValueError('Reranker must return one finite score in [0, 1] per candidate')
        weight = settings.RERANK_WEIGHT
        ranked = [replace(hit, hybrid_score=float(weight * score + (1 - weight) * hit.hybrid_score),
                          reranker_score=float(score),
                          ranking={**hit.ranking, 'reranker_score': float(score),
                                   'first_stage_score': hit.hybrid_score, 'candidate_count': len(rows),
                                   'reranker_weight': weight}) for hit, score in zip(candidates, scores)]
        return sorted(ranked, key=lambda hit: (-hit.hybrid_score, hit.id))[:top_k]

    def configuration(self):
        return {**super().configuration(), 'reranker': {
            **self.reranker.settings, 'weight': settings.RERANK_WEIGHT,
            'candidates_per_signal': settings.CANDIDATES_PER_SIGNAL,
            'candidate_signals': ['original semantic', 'contextual semantic', 'lexical', 'hybrid'],
            'input': 'Original current message text plus sender and chat date; no neighbor text or thread labels',
            'constraints': 'Applied before candidate selection; never relaxed',
            'selection': 'One model and configuration declared before supplemental scoring; no weight sweep'}}
