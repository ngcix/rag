# RAG Project Plan

## Goals

Build a local-first RAG system for one corpus database containing many documents. Users ingest PDF, DOCX, Markdown, and text files into the same database, then search it through either the CLI or FastAPI.

Priorities:

- Keep Python code short, modular, and single-purpose.
- Share business logic between CLI and FastAPI.
- Return source file, page number, and chunk ID with every search result.
- Keep storage inspectable with SQL.
- Deliver text-document ingestion and retrieval first. Images, OCR, tags, and knowledge enrichment come later.

## Architecture

~~~text
CLI command ----+
                +-- use_cases -- documents / retrieval / storage
FastAPI route --+

knowledge.duckdb  <- metadata, chunks, FTS/BM25, index state
knowledge.faiss   <- dense vectors keyed by stable chunk IDs
~~~

The command and api packages are adapters. They parse or validate input, create request models, call use cases, and render output.

The use_cases package orchestrates application behavior. A use case must not import argparse, FastAPI, or Uvicorn.

The documents, retrieval, and storage packages contain concrete implementations. This keeps the CLI/API contracts stable if FAISS is replaced with Qdrant later.

## Selected Technology Stack

| Layer | Technology | Rationale |
| --- | --- | --- |
| Runtime | Python 3.11+ | Modern type hints, tomllib, and a stable ecosystem. |
| CLI | argparse | Standard library, compatible with the LogDB style, and smaller than a separate CLI framework. |
| HTTP API | FastAPI and Uvicorn | Pydantic validation, generated OpenAPI, and thin adapters. |
| API schemas | Pydantic v2 | Shared validation and explicit request/response contracts. |
| PDF reader | PyMuPDF | Page-level text extraction preserves page numbers for citations. |
| DOCX reader | python-docx | Simple paragraph extraction, sufficient for the MVP. |
| Markdown/text reader | pathlib and the standard library | No additional dependency. |
| Chunking | Internal implementation | Paragraph-aware chunks with overlap; LangChain is not required for the MVP. |
| Embedding | sentence-transformers | Standard adapter for local or Hugging Face embedding models. |
| Metadata database | DuckDB | One inspectable database file, similar to LogDB. |
| Lexical search | DuckDB FTS extension | Built-in BM25 instead of a custom in-memory index. |
| Dense search | FAISS IndexIDMap2 and IndexFlatIP | Fast local search with a small implementation. Normalized embeddings give cosine similarity. |
| Hybrid fusion | Reciprocal Rank Fusion (RRF) | Merges BM25 and dense rankings without score-scale calibration. |
| Tests | pytest and FastAPI TestClient | Unit tests for modules and HTTP contracts. |
| Formatting/linting | Ruff | Fast checks with compact configuration. |

The MVP does not include LangChain, ChromaDB, aiohttp, image extraction, OCR, sequence charts, tags, knowledge enrichment, multi-query retrieval, or a reranker.

## Storage Model

Each corpus uses a database path and a matching FAISS index.

~~~text
data/
  wifi.duckdb
  wifi.faiss
~~~

DuckDB stores the following logical tables.

~~~sql
documents(
  document_id, source_path, content_hash, file_type,
  page_count, ingested_at, updated_at
)

chunks(
  chunk_id, document_id, ordinal, page_number,
  char_start, char_end, content, metadata_json
)

index_state(
  revision, embedding_model, embedding_dimension,
  chunk_count, updated_at
)
~~~

A DuckDB FTS index is built over chunks.content. FAISS stores vectors and stable numeric IDs only. The mapping from chunk ID to the FAISS numeric ID stays in DuckDB; pickle is not used.

For the MVP, ingestion rebuilds the FAISS index into a temporary file and atomically swaps it in. This prevents the DuckDB database and FAISS file from drifting apart. Incremental indexing is deferred until a benchmark proves it is needed.

## Target Module Layout

~~~text
src/rag/
  __main__.py                 # python -m rag
  cli.py                      # register CLI parsers
  config.py                   # paths and embedding configuration

  command/
    ingest.py                 # argparse adapter -> use case
    query.py                  # argparse adapter -> use case
    inspect.py                # argparse adapter -> use case
    serve.py                  # start Uvicorn

  use_cases/
    models.py                 # request and response models
    ingest.py                 # ingest_documents()
    search.py                 # search_documents()
    inspect.py                # inspect_database()

  documents/
    models.py                 # SourceDocument, DocumentPage, Chunk
    reader.py                 # choose reader by extension
    pdf.py                    # PyMuPDF reader
    docx.py                   # python-docx reader
    text.py                   # Markdown and text reader
    chunking.py               # page/section chunking

  retrieval/
    embedder.py               # SentenceTransformer adapter
    hybrid.py                 # RRF fusion
    models.py                 # SearchHit and candidate models

  storage/
    database.py               # DuckDB schema, transactions, and FTS
    faiss_index.py            # load, build, search, and atomic save
    repository.py             # document and chunk persistence

  api/
    app.py                    # FastAPI routes
    schemas.py                # HTTP Pydantic schemas

tests/
  documents/
  retrieval/
  storage/
  use_cases/
  api/
~~~

Module rules:

- Split readers by file type because dependencies and metadata differ.
- Do not split files only by line count; split when responsibilities or dependencies differ.
- Adapters call use cases only; they do not call FAISS or DuckDB directly.
- Avoid global singletons for settings, the embedder, or the index. Create dependencies at the composition root and pass them into use cases.

## Use Case Contracts

### Ingest

~~~python
def ingest_documents(request: IngestRequest) -> IngestReport: ...
~~~

The request contains a source file or directory, a database path, and a replace flag.

1. Scan supported files.
2. Compute SHA-256 and skip unchanged files.
3. Read files into page or section units with metadata.
4. Build stable chunks.
5. Generate embeddings for new chunks.
6. Upsert documents and chunks into DuckDB and atomically rebuild FAISS.
7. Return counts for added, updated, skipped, and failed files plus the new index revision.

### Search

~~~python
def search_documents(request: SearchRequest) -> SearchResponse: ...
~~~

1. Embed the query.
2. Retrieve dense candidates from FAISS.
3. When hybrid is enabled, retrieve BM25 candidates through DuckDB FTS.
4. Fuse and deduplicate candidates with RRF.
5. Read chunk content and citation data from DuckDB.
6. Return ranked search results.

### Inspect

~~~python
def inspect_database(request: InspectRequest) -> DatabaseInfo: ...
~~~

Returns the database path, document count, chunk count, embedding model and dimension, FTS status, and index revision.

## CLI and HTTP Contract

CLI:

~~~bash
rag ingest ./docs --database data/wifi.duckdb
rag query "authentication flow" --database data/wifi.duckdb --top-k 5
rag query "Figure 4.1" --database data/wifi.duckdb --hybrid
rag inspect --database data/wifi.duckdb
rag serve --host 127.0.0.1 --port 8000
~~~

HTTP:

~~~text
GET  /health
POST /ingest
POST /query
GET  /databases/{name}
~~~

For the MVP, POST /ingest accepts a local path that the server is explicitly allowed to access. File upload and an asynchronous job queue are later phases.

CLI and FastAPI return the same logical result schema.

~~~json
{
  "query": "authentication flow",
  "database": "data/wifi.duckdb",
  "results": [
    {
      "rank": 1,
      "chunk_id": "chunk-id",
      "score": 0.84,
      "content": "text excerpt",
      "source_path": "spec.pdf",
      "page_number": 12
    }
  ]
}
~~~

## Delivery Phases

1. Refactor the skeleton: move argparse wrappers into command and replace placeholder use cases with plain Python request/response models.
2. Implement the DuckDB schema, document registry, and text/Markdown reader.
3. Implement PDF/DOCX readers and page-aware chunking.
4. Implement embedding and FAISS build/search.
5. Implement semantic search through CLI and FastAPI.
6. Add DuckDB FTS and RRF hybrid retrieval.
7. Add tests, a benchmark corpus, and user documentation.
8. Evaluate Qdrant, a reranker, OCR, or image processing only after measuring a real need.

## When to Consider Qdrant

Do not use Qdrant in the MVP. Replace the storage implementation with Qdrant when concurrent writers/readers, complex payload filters, a large corpus, or native dense+sparse hybrid search is required.

This replacement must be isolated to storage and retrieval; CLI, FastAPI, and use case contracts remain unchanged.
## Single-Machine Deployment and Capacity

Target hardware: an Intel i7 with 6 physical cores, 16 GB RAM, and 500 GB storage.

This machine is suitable for a local corpus and up to 2,000 registered users when traffic is moderate. It is not suitable for 2,000 CPU-bound embedding requests actively executing at the same moment. User count, concurrent open connections, active requests, and requests per second are separate capacity measurements.

### Main bottleneck

FAISS and DuckDB retrieval are comparatively inexpensive. Query embedding on CPU is the dominant cost. PDF/DOCX ingestion is also CPU and I/O intensive and must not run on the request path.

A 768-dimensional float32 FAISS vector takes about 3 KiB before ID and application overhead. One million vectors therefore need about 2.86 GiB for raw vectors alone. A 384-dimensional model halves that requirement to about 1.43 GiB. FAISS indexes are memory-resident, so 500 GB disk capacity does not eliminate the 16 GB RAM constraint.

The previous 305M-parameter GTE model is usable for offline ingestion but is too expensive as the default CPU query model for this hardware under concurrent load.

### Recommended deployment shape

~~~text
Clients
  -> reverse proxy with TLS and request limits
  -> one FastAPI/Uvicorn process
  -> bounded query queue and embedding batcher
  -> DuckDB + FAISS loaded once in the process

Separate background ingestion worker
  -> document readers -> embedding -> atomic index rebuild
~~~

Use one API worker initially. Multiple Uvicorn workers duplicate the loaded model and FAISS index in RAM, which is unsafe on a 16 GB machine. Do not increase workers before measuring memory.

The API accepts many waiting connections, but the application must bound active CPU work. Start with:

- Maximum 4 active embedding jobs.
- Micro-batching with a short wait window and a maximum batch size of 8 to 16 queries.
- A bounded queue. Return HTTP 429 or 503 with Retry-After when it is full.
- A query timeout, input-length limit, and top-k limit.
- A small TTL/LRU cache for repeated queries.
- A separate, serialized ingestion worker. POST /ingest should return a job ID rather than process documents synchronously.

Use an ONNX-optimized and quantized sentence-transformers model for CPU serving. Select a multilingual model with approximately 384 dimensions and benchmark it on the real documents; do not hard-code one large model path.

### Capacity gate

Before claiming support for 2,000 users, define an SLA and benchmark the target corpus:

1. Peak requests per second and burst size.
2. Query length distribution and top-k.
3. P50, P95, and P99 latency.
4. Queue wait time, timeout rate, and HTTP 429/503 rate.
5. RAM RSS during ingestion and peak query traffic.
6. Number of documents and chunks.

Scale to a second machine or a separate vector service only after this benchmark. Qdrant can help with independent vector-service scaling and native hybrid search, but it does not remove the CPU embedding bottleneck.
## Enterprise License and Supply-Chain Policy

This project must have no required paid cloud service and must use only dependencies approved for enterprise use. This is an engineering policy, not legal advice; the organization legal and open-source review process remains the final authority.

### Default allowlist

Allow only these SPDX families unless an explicit exception is approved:

- MIT
- BSD-2-Clause or BSD-3-Clause
- Apache-2.0
- Python-2.0 or PSF-2.0 for the Python runtime

Reject copyleft, source-available, commercial-only, and unknown licenses from runtime dependencies by default. This includes AGPL, GPL, LGPL, SSPL, Elastic License, Business Source License, and packages or models without a clear license.

### Approved MVP stack

| Component | License family | Decision |
| --- | --- | --- |
| FastAPI and Pydantic | MIT | Approved |
| Uvicorn | BSD-family | Approved after version-specific review |
| DuckDB | MIT | Approved |
| FAISS | MIT | Approved |
| sentence-transformers | Apache-2.0 | Approved; each model remains a separate review item |
| ONNX Runtime | MIT | Approved |
| pypdf | BSD-3-Clause | Approved PDF text reader |
| python-docx | MIT | Approved |
| pytest and Ruff | Permissive-license dependencies only | Approve after lockfile review |
| Qdrant, if adopted later | Apache-2.0 | Eligible; not required for the MVP |

### Explicit exclusions and overrides

PyMuPDF is excluded. Its open-source distribution is AGPL and its proprietary use path requires a commercial license. The PDF reader selected in the earlier technology table is therefore overridden: use pypdf for the MVP.

Do not use PyInstaller as a required runtime or build dependency. Its GPL exception can permit commercial bundling, but it creates unnecessary license-review work and is not needed for the Python-first MVP. Cython is Apache-2.0 but is also deferred until profiling proves a performance need.

### Model and artifact controls

Model weights, tokenizers, ONNX exports, training datasets, and fonts are independent third-party artifacts. A permissive Python library does not make an arbitrary model enterprise-approved.

For every model version:

1. Record model name, revision hash, source URL, SPDX license, and required attribution.
2. Verify that commercial/internal use is allowed by its model card and upstream terms.
3. Download through an approved internal artifact repository, never on a production request path.
4. Pin the exact revision and checksum in the lockfile or model manifest.
5. Keep an SBOM and third-party-notice file with the release artifact.

No external model API, cloud vector database, telemetry service, or automatic model download is part of the MVP.
## Large-Corpus Ingestion and Document Updates

The target corpus can contain hundreds of documents with thousands of pages each. Therefore ingestion must be streaming, resumable, idempotent, and incremental. It must never load a complete document or the complete corpus into Python memory.

### Data identity and versioning

Use three levels of identity:

- A document has a stable document ID and a whole-file SHA-256 hash.
- Each extracted page has a normalized-text hash.
- Each chunk has a stable chunk ID and a unique int64 vector ID.

When the whole-file hash is unchanged, skip the document. When a file changes, compare page hashes and embed only changed pages plus adjacent pages affected by chunk overlap. Keeping chunks within a page makes page-level replacement safe and preserves page citations.

Do not update a document in place. Create a staged document version, validate all pages and chunks, then atomically mark the new version active. The previous version remains searchable until commit and is retired afterwards. A failed job leaves the previous version active.

### Streaming ingestion flow

1. Create an ingest job with a checkpoint in DuckDB.
2. Read one page or small page batch at a time.
3. Normalize text, hash the page, and skip unchanged content.
4. Create chunks in a bounded batch.
5. Embed one bounded batch, for example 32 to 128 chunks.
6. Persist staged document, page, chunk, and vector metadata.
7. Periodically save the checkpoint so the job can resume after a restart.
8. Activate the new document version only after its final batch succeeds.

A scanned PDF with no extractable text is recorded as a skipped or failed document. OCR is a separate, license-reviewed future capability.

### Base and delta indexes

Do not rebuild the complete FAISS index for every new or updated document.

~~~text
base.faiss          immutable compacted index
delta-001.faiss     vectors from recent ingest/update jobs
delta-002.faiss     newer vectors
vector manifest     active base/delta segment revisions
DuckDB              document versions, active chunks, vector IDs
~~~

Search the base index and active delta indexes in parallel, over-fetch candidates, then use DuckDB to discard inactive or superseded chunks before final ranking.

New documents and new document versions append to a delta index. A background compaction job merges base and delta segments when the delta size or inactive-vector ratio crosses a configured threshold. Compaction creates a new base index and manifest, then atomically swaps the manifest. Search requests continue using the previous manifest until the swap succeeds.

Store raw normalized vectors in immutable float32 segment files or a DuckDB binary table, never pickle. Compaction rebuilds FAISS from those stored vectors without calling the embedding model again. Re-embedding the entire corpus is required only when the embedding model or chunking policy changes.

### Index choice

Begin with IDMap plus Flat only for a measured small corpus. FAISS supports caller-provided int64 IDs through an IDMap wrapper.

For a corpus whose benchmark exceeds the latency budget, build the immutable base as an IVF index trained from a representative sample. Keep delta segments small and exact. IVF supports vector IDs natively and offers a latency/recall tradeoff through nprobe. HNSW is not the default update index because FAISS HNSW does not support vector removal.

The exact thresholds for Flat, IVF, delta compaction, batch size, and nprobe are configuration values selected by benchmark, not hard-coded project constants.

### Query and ingest isolation

Search is the priority workload. Ingestion is rare and runs with lower priority:

- Run at most one ingest job on this hardware.
- Limit ingestion embedding threads so query embedding retains CPU capacity.
- Keep the current search manifest read-only for the duration of a request.
- Publish index changes only through an atomic manifest revision.
- Expose ingest job status through CLI and an admin-only API endpoint.

This design handles large files, supports safe replacement of changed documents, and avoids both full-corpus re-embedding and query downtime.
