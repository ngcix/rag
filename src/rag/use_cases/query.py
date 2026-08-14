"""Document-query use case placeholder."""

import argparse
from typing import Any


def run(args: argparse.Namespace) -> int:
    query(args.text, collection=args.collection, top_k=args.top_k, hybrid=args.hybrid)
    return 0


def query(text: str, *, collection: str, top_k: int, hybrid: bool = False) -> list[dict[str, Any]]:
    raise NotImplementedError("document query")
