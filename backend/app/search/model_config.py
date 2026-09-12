"""Pinned local embedding configuration, fixed before contextual scoring."""

from pathlib import Path
import re

MODEL_ID = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
MODEL_REVISION = 'e8f8c211226b894fcb81acc59f3b34ba3efd5f42'
ROOT = Path(__file__).resolve().parents[3]
MODEL_DIRECTORY = ROOT / '.cache' / 'models' / MODEL_REVISION
EMBEDDING_CACHE = ROOT / '.cache' / 'embeddings'
MAX_SEQUENCE_LENGTH = 256
BATCH_SIZE = 32
CPU_THREADS = 4
MODEL_FILES = (
    'config.json', 'config_sentence_transformers.json', 'modules.json',
    'sentence_bert_config.json', '1_Pooling/config.json',
    'tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json',
    'sentencepiece.bpe.model', 'model.safetensors',
)


def validate_model_manifest(manifest):
    """Reject malformed cache metadata before loading weights or hashing paths."""
    if (not isinstance(manifest, dict)
            or manifest.get('model_id') != MODEL_ID
            or manifest.get('revision') != MODEL_REVISION
            or not isinstance(manifest.get('sha256'), dict)
            or set(manifest['sha256']) != set(MODEL_FILES)
            or any(not isinstance(digest, str) or re.fullmatch(r'[0-9a-f]{64}', digest) is None
                   for digest in manifest['sha256'].values())):
        raise ValueError('Invalid local model manifest. Restore a clean model cache and rerun '
                         'python -m scripts.prepare_model from backend.')
