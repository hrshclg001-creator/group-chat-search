"""Evaluate the predeclared reranker on the unchanged assessment and bilingual set.

Run from root: python -m evaluation.evaluate_reranked
"""

from datetime import datetime, timezone
import hashlib
import json

from backend.app.search.corpus import load_corpus
from backend.app.search.reranked import RerankedSearch
from evaluation.evaluate_bilingual import ROOT, load_queries, measure
from evaluation.validate_queries import validate_files


def main():
    validate_files()
    engine = RerankedSearch(load_corpus())
    queries = json.loads((ROOT / 'evaluation/queries.json').read_text(encoding='utf-8'))
    report = measure(engine, queries)
    report['measured_at_utc'] = datetime.now(timezone.utc).isoformat()
    report['input_freeze'] = json.loads((ROOT / 'evaluation/freeze_manifest.json').read_text(encoding='utf-8'))
    source_paths = sorted((ROOT / 'backend/app').rglob('*.py')) + sorted((ROOT / 'evaluation').glob('*.py'))
    report['source_sha256'] = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in source_paths}
    (ROOT / 'results/reranker_experiment.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('ASSESSMENT', report['metrics'], flush=True)
    queries, manifest = load_queries()
    report = {'input_sha256': manifest, 'reports': {'reranked': measure(engine, queries)}}
    (ROOT / 'results/bilingual_reranked.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('BILINGUAL', report['reports']['reranked']['metrics'], report['reports']['reranked']['by_language'], flush=True)
    validate_files()
    load_queries()


if __name__ == '__main__':
    main()
