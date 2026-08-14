"""Document-ingestion use case placeholder."""

import argparse


def run(args: argparse.Namespace) -> int:
    ingest(args.source, collection=args.collection, replace=args.replace)
    return 0


def ingest(source: str, *, collection: str, replace: bool = False) -> None:
    raise NotImplementedError("document ingestion")
