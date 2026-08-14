"""Command-line adapter for RAG use cases."""

import argparse
import sys

from rag.use_cases import ingest, inspect, query


def parser_builder() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rag")
    commands = parser.add_subparsers(dest="command", required=True)

    ingest_parser = commands.add_parser("ingest", help="Index documents")
    ingest_parser.add_argument("source")
    ingest_parser.add_argument("--collection", default="default")
    ingest_parser.add_argument("--replace", action="store_true")
    ingest_parser.set_defaults(handler=ingest.run)

    query_parser = commands.add_parser("query", help="Query indexed documents")
    query_parser.add_argument("text")
    query_parser.add_argument("--collection", default="default")
    query_parser.add_argument("--top-k", type=int, default=5)
    query_parser.add_argument("--hybrid", action="store_true")
    query_parser.set_defaults(handler=query.run)

    inspect_parser = commands.add_parser("inspect", help="Show collection metadata")
    inspect_parser.add_argument("--collection", default="default")
    inspect_parser.set_defaults(handler=inspect.run)

    serve_parser = commands.add_parser("serve", help="Start the FastAPI server")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.set_defaults(handler=_serve)
    return parser


def _serve(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run("rag.api.app:app", host=args.host, port=args.port)
    return 0


def main() -> int:
    args = parser_builder().parse_args()
    try:
        return int(args.handler(args) or 0)
    except NotImplementedError as error:
        print(f"not implemented: {error}", file=sys.stderr)
        return 2
