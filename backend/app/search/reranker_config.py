"""One predeclared local reranking configuration; no per-query exceptions."""

from .model_config import ROOT

MODEL_ID = 'cross-encoder/mmarco-mMiniLMv2-L12-H384-v1'
MODEL_REVISION = '1427fd652930e4ba29e8149678df786c240d8825'
WEIGHTS_SHA256 = '5daeca2481a76b5976a2bdc32f0a78532b6716da4f8cd3ff59460ef8d2f359b4'
MODEL_DIRECTORY = ROOT / '.cache' / 'models' / MODEL_REVISION
MODEL_FILES = ('config.json', 'model.safetensors', 'sentencepiece.bpe.model',
               'special_tokens_map.json', 'tokenizer.json', 'tokenizer_config.json')
CANDIDATES_PER_SIGNAL = 128
MAX_SEQUENCE_LENGTH = 256
BATCH_SIZE = 16
RERANK_WEIGHT = 0.85
