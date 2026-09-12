"""Prepare the pinned public multilingual reranker; never called by requests."""

import hashlib
import json
import urllib.request

from app.search.reranker_config import MODEL_DIRECTORY, MODEL_FILES, MODEL_ID, MODEL_REVISION
from app.search.reranked import verify_manifest


def prepare_model():
    MODEL_DIRECTORY.mkdir(parents=True, exist_ok=True)
    manifest_path = MODEL_DIRECTORY / 'download_manifest.json'
    if manifest_path.exists():
        verify_manifest(MODEL_DIRECTORY)
        print('Pinned reranker cache verified', flush=True)
        return
    hashes = {}
    for name in MODEL_FILES:
        path = MODEL_DIRECTORY / name
        if not path.exists():
            print(f'Downloading reranker {name}', flush=True)
            part = path.with_suffix(path.suffix + '.part')
            url = f'https://huggingface.co/{MODEL_ID}/resolve/{MODEL_REVISION}/{name}?download=true'
            with urllib.request.urlopen(url, timeout=120) as response, part.open('wb') as output:
                for chunk in iter(lambda: response.read(1024 * 1024), b''):
                    output.write(chunk)
            part.replace(path)
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        hashes[name] = digest.hexdigest()
    manifest_path.write_text(json.dumps({'model_id': MODEL_ID, 'revision': MODEL_REVISION,
                                         'sha256': hashes}, indent=2) + '\n', encoding='utf-8')
    verify_manifest(MODEL_DIRECTORY)
    print('Reranker ready for offline inference', flush=True)


if __name__ == '__main__':
    prepare_model()
