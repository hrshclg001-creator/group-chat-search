"""Offline pinned sentence-transformer and content-keyed embedding cache."""

import hashlib
import json
from importlib.metadata import version

import numpy as np

from .model_config import (
    BATCH_SIZE, CPU_THREADS, EMBEDDING_CACHE, MAX_SEQUENCE_LENGTH,
    MODEL_DIRECTORY, MODEL_FILES, MODEL_ID, MODEL_REVISION,
)


def normalize_vectors(vectors):
    matrix = np.asarray(vectors, dtype=np.float32)
    if matrix.ndim != 2 or not np.isfinite(matrix).all():
        raise ValueError('Embedding matrix must be finite and two-dimensional')
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if (norms <= 0).any():
        raise ValueError('Embedding vectors must be nonzero')
    return matrix / norms


class LocalEncoder:
    def __init__(self):
        manifest_path = MODEL_DIRECTORY / 'download_manifest.json'
        if not manifest_path.is_file() or not all((MODEL_DIRECTORY / file).is_file() for file in MODEL_FILES):
            raise FileNotFoundError('Prepare the model first: cd backend; python -m scripts.prepare_model')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest['model_id'] != MODEL_ID or manifest['revision'] != MODEL_REVISION:
            raise ValueError('Local model manifest does not match the pinned revision')
        # Hash the actual local files once per encoder to avoid accepting altered weights.
        for name in MODEL_FILES:
            digest = hashlib.sha256()
            with (MODEL_DIRECTORY / name).open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            if digest.hexdigest() != manifest['sha256'][name]:
                raise ValueError(f'Local model file hash mismatch: {name}')
        import torch
        from sentence_transformers import SentenceTransformer

        torch.set_num_threads(CPU_THREADS)
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True)
        self.model = SentenceTransformer(str(MODEL_DIRECTORY), device='cpu',
                                         local_files_only=True, trust_remote_code=False)
        self.model.max_seq_length = MAX_SEQUENCE_LENGTH
        self.model.eval()
        self.tokenizer = self.model.tokenizer
        self.max_sequence_length = MAX_SEQUENCE_LENGTH
        self.settings = {
            'model_id': MODEL_ID, 'revision': MODEL_REVISION,
            'model_file_sha256': manifest['sha256'],
            'max_sequence_length': MAX_SEQUENCE_LENGTH,
            'packaged_max_sequence_length': 128,
            'batch_size': BATCH_SIZE, 'device': 'cpu', 'cpu_threads': CPU_THREADS,
            'dtype': 'float32', 'normalize_embeddings': True,
            'dependencies': {name: version(name) for name in
                             ('sentence-transformers', 'transformers', 'torch', 'numpy', 'huggingface-hub')},
        }

    def encode(self, texts):
        return self.model.encode(list(texts), batch_size=BATCH_SIZE,
                                 show_progress_bar=False, convert_to_numpy=True,
                                 normalize_embeddings=True)


def cached_embeddings(encoder, texts, cache_dir=EMBEDDING_CACHE):
    key_payload = json.dumps({'encoder': encoder.settings, 'texts': list(texts)},
                             ensure_ascii=False, sort_keys=True).encode('utf-8')
    key = hashlib.sha256(key_payload).hexdigest()
    destination = cache_dir / f'{key}.npz'
    if destination.exists():
        with np.load(destination, allow_pickle=False) as saved:
            matrix = saved['embeddings']
            matrix_hash = str(saved['matrix_sha256'])
        if matrix.ndim != 2 or matrix.shape[0] != len(texts):
            raise ValueError('Cached embedding shape does not match the index')
        if (not np.isfinite(matrix).all() or not np.allclose(np.linalg.norm(matrix, axis=1), 1, atol=1e-5)
                or hashlib.sha256(matrix.tobytes()).hexdigest() != matrix_hash):
            raise ValueError('Cached embedding integrity check failed')
        return matrix, key
    batches = []
    for start in range(0, len(texts), 256):
        batch = normalize_vectors(encoder.encode(texts[start:start + 256]))
        batches.append(batch)
        print(f'Embedded {min(start + 256, len(texts))}/{len(texts)} messages', flush=True)
    matrix = np.vstack(batches)
    cache_dir.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix('.npz.part')
    with temporary.open('wb') as stream:
        np.savez_compressed(stream, embeddings=matrix, matrix_sha256=hashlib.sha256(matrix.tobytes()).hexdigest())
    temporary.replace(destination)
    return matrix, key
