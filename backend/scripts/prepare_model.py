"""Download the pinned public model once; inference subsequently stays offline.

From backend: python -m scripts.prepare_model
"""

import hashlib
import json
import urllib.request
from pathlib import Path

from app.search.model_config import MODEL_DIRECTORY, MODEL_FILES, MODEL_ID, MODEL_REVISION


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_model():
    MODEL_DIRECTORY.mkdir(parents=True, exist_ok=True)
    manifest_path = MODEL_DIRECTORY / 'download_manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if (manifest['model_id'] != MODEL_ID or manifest['revision'] != MODEL_REVISION
                or set(manifest['sha256']) != set(MODEL_FILES)):
            raise ValueError('Model manifest does not match the pinned configuration')
        for name, digest in manifest['sha256'].items():
            if file_hash(MODEL_DIRECTORY / name) != digest:
                raise ValueError(f'Model cache hash mismatch: {name}')
        print(f'Pinned model cache verified: {MODEL_DIRECTORY}', flush=True)
        return
    hashes = {}
    for name in MODEL_FILES:
        destination = MODEL_DIRECTORY / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            print(f'Downloading {name} from pinned revision {MODEL_REVISION}', flush=True)
            part = destination.with_suffix(destination.suffix + '.part')
            url = f'https://huggingface.co/{MODEL_ID}/resolve/{MODEL_REVISION}/{name}?download=true'
            with urllib.request.urlopen(url, timeout=120) as response, part.open('wb') as output:
                total = 0
                announced = 0
                for chunk in iter(lambda: response.read(1024 * 1024), b''):
                    output.write(chunk)
                    total += len(chunk)
                    if total - announced >= 32 * 1024 * 1024:
                        print(f'  {name}: {total // (1024 * 1024)} MiB', flush=True)
                        announced = total
            part.replace(destination)
        hashes[name] = file_hash(destination)
    manifest = {'model_id': MODEL_ID, 'revision': MODEL_REVISION, 'sha256': hashes}
    manifest_path.write_bytes((json.dumps(manifest, indent=2) + '\n').encode('utf-8'))
    print(f'Model ready for offline use: {MODEL_DIRECTORY}', flush=True)


if __name__ == '__main__':
    prepare_model()
