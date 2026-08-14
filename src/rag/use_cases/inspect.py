"""Collection-inspection use case placeholder."""

import argparse
from typing import Any


def run(args: argparse.Namespace) -> int:
    inspect_collection(args.collection)
    return 0


def inspect_collection(collection: str) -> dict[str, Any]:
    raise NotImplementedError("collection inspection")
