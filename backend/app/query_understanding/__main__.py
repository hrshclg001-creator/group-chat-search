"""Print parsed queries without loading a search index or embedding model."""

import argparse
import json

from .parser import DEFAULT_METADATA_PATH, QueryParser


def main():
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument('queries', nargs='+')
    arguments.add_argument('--metadata', default=DEFAULT_METADATA_PATH)
    args = arguments.parse_args()
    parser = QueryParser.from_metadata(args.metadata)
    print(json.dumps([parser.parse(query).to_dict() for query in args.queries], indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
