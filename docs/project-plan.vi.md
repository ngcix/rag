# RAG project plan

## 1. M?c ti?u

X?y d?ng m?t RAG local-first cho **m?t corpus database ch?a nhi?u t?i li?u**. Ng??i d?ng c? th? ingest PDF, DOCX, Markdown v? text v?o c?ng database, sau ?? query t? CLI ho?c FastAPI.

M?c ti?u ?u ti?n:

- Python code ng?n, module nh? v? m?t tr?ch nhi?m r? r?ng.
- CLI v? FastAPI g?i c?ng use case; kh?ng duplicate business logic.
- K?t qu? search lu?n tr? ngu?n, trang v? chunk ID ?? tr?ch d?n.
- Storage minh b?ch, inspect ???c b?ng SQL.
- MVP tr??c: text document ingestion v? retrieval. ?nh, OCR, tag v? knowledge enrichment ?? sau.

## 2. Ki?n tr?c

~~~text
CLI command ??
             ??? use_cases ?? documents / retrieval / storage
FastAPI route?

knowledge.duckdb  <?? metadata, chunks, FTS/BM25, index state
knowledge.faiss   <?? dense vectors indexed by stable chunk id
~~~

`command/` v? `api/` l? adapter. Ch?ng ch? parse/validate input, t?o request model, g?i use case v? render response.

`use_cases/` ?i?u ph?i nghi?p v?. Use case kh?ng import `argparse`, FastAPI hay Uvicorn.

`documents/`, `retrieval/` v? `storage/` ch?a implementation c? th?. Nh? v?y c? th? thay FAISS b?ng Qdrant sau n?y m? kh?ng ??i CLI/API contract.

## 3. C?ng ngh? ???c ch?n

| T?ng | C?ng ngh? | L? do |
| --- | --- | --- |
| Runtime | Python 3.11+ | Type hints hi?n ??i, `tomllib`, dependency ecosystem ?n ??nh. |
| CLI | `argparse` | C? s?n trong standard library, ph? h?p m?u `logdb`, ?t code h?n Typer. |
| HTTP API | FastAPI + Uvicorn | Pydantic validation, OpenAPI t? sinh, adapter m?ng. |
| API schema | Pydantic v2 | Request/response contract d?ng chung v? validation. |
| PDF reader | PyMuPDF | Tr?ch text theo page, gi? ???c page number ?? citation. |
| DOCX reader | python-docx | ??c paragraph DOCX ??n gi?n, ?? MVP. |
| Markdown/text reader | Standard library `pathlib` | Kh?ng c?n th?m dependency. |
| Chunking | Code n?i b? | Chunk theo k? t?/?o?n v?n, c? overlap; kh?ng c?n LangChain ? MVP. |
| Embedding | sentence-transformers | Interface chu?n ?? n?p embedding model local ho?c Hugging Face. |
| Metadata database | DuckDB | M?t file database, SQL inspect/debug thu?n ti?n nh? `logdb`. |
| Lexical search | DuckDB `fts` extension | D?ng BM25 c? s?n thay v? t? x?y index in-memory. |
| Dense vector search | FAISS (`IndexIDMap2` + `IndexFlatIP`) | Local, nhanh, code ?t; cosine similarity qua normalized embedding. |
| Hybrid fusion | Reciprocal Rank Fusion (RRF) | Gh?p ranking dense v? BM25, kh?ng ph?i chu?n h?a hai lo?i score. |
| Test | pytest + FastAPI TestClient | Unit test module v? API contract. |
| Format/lint | Ruff | Ki?m tra nhanh, c?u h?nh g?n. |

Kh?ng d?ng trong MVP: LangChain, ChromaDB, aiohttp, image extraction, OCR, sequence charts, tags/knowledge, multi-query v? reranker.

## 4. Storage model

M?i corpus t??ng ?ng m?t database path, v? d?:

~~~text
data/
  wifi.duckdb
  wifi.faiss
~~~

DuckDB ch?a ba nh?m d? li?u ch?nh:

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

DuckDB FTS index ???c t?o tr?n `chunks.content`. FAISS ch? l?u vector v? stable numeric ID. Quan h? `chunk_id` <-> FAISS numeric ID ???c l?u trong DuckDB, kh?ng d?ng pickle.

MVP d?ng rebuild-to-temp-and-swap khi index thay ??i ?? tr?nh database v? `.faiss` b? l?ch tr?ng th?i. Incremental indexing ch? th?m khi corpus ?? l?n v? c? benchmark ch?ng minh c?n thi?t.

## 5. Module layout m?c ti?u

~~~text
src/rag/
  __main__.py                 # python -m rag
  cli.py                      # ??ng k? CLI parser
  config.py                   # paths v? model configuration

  command/
    ingest.py                 # argparse adapter -> use case
    query.py                  # argparse adapter -> use case
    inspect.py                # argparse adapter -> use case
    serve.py                  # ch?y Uvicorn

  use_cases/
    models.py                 # IngestRequest/Report, SearchRequest/Response
    ingest.py                 # ingest_documents()
    search.py                 # search_documents()
    inspect.py                # inspect_database()

  documents/
    models.py                 # SourceDocument, DocumentPage, Chunk
    reader.py                 # ch?n reader theo extension
    pdf.py                    # PyMuPDF reader
    docx.py                   # python-docx reader
    text.py                   # .md v? .txt reader
    chunking.py               # chunk page/section text

  retrieval/
    embedder.py               # SentenceTransformer adapter
    hybrid.py                 # RRF fusion
    models.py                 # SearchHit, candidate types

  storage/
    database.py               # DuckDB schema, transaction, FTS
    faiss_index.py            # load, build, search, atomic save
    repository.py             # document/chunk persistence

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

Module split rule:

- T?ch reader theo file type v? dependency v? metadata kh?c nhau.
- Kh?ng t?ch file ch? v? ?? d?i; ch? t?ch khi responsibility ho?c dependency kh?c nhau.
- M?i adapter file ch? g?i use case, kh?ng g?i FAISS/DuckDB tr?c ti?p.
- Kh?ng t?o global singleton cho settings, embedder ho?c index. Kh?i t?o dependency t?i composition root v? truy?n v?o use case.

## 6. Use case contracts

### Ingest

~~~python
def ingest_documents(request: IngestRequest) -> IngestReport: ...
~~~

Input g?m source file/directory, database path v? c? replace. Flow:

1. Qu?t file ???c h? tr?.
2. T?nh SHA-256 ?? skip file kh?ng ??i.
3. Reader t?ch th?nh page/section c? metadata.
4. Chunker t?o chunk ?n ??nh.
5. Embed chunks m?i.
6. Upsert document/chunks v?o DuckDB v? t?o l?i FAISS atomically.
7. Tr? report: added, updated, skipped, failed v? index revision.

### Search

~~~python
def search_documents(request: SearchRequest) -> SearchResponse: ...
~~~

Flow:

1. Embed query.
2. L?y dense candidates t? FAISS.
3. N?u `hybrid=True`, l?y BM25 candidates t? DuckDB FTS.
4. RRF fusion v? deduplicate theo chunk ID.
5. ??c chunk/source/page t? DuckDB.
6. Tr? result c? citation metadata.

### Inspect

~~~python
def inspect_database(request: InspectRequest) -> DatabaseInfo: ...
~~~

Tr? database path, document count, chunk count, embedding model/dimension, FTS status v? index revision.

## 7. CLI v? HTTP contract

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

`POST /ingest` nh?n ???ng d?n local ?? ???c server cho ph?p truy c?p trong MVP. File upload v? asynchronous job queue l? phase sau.

CLI query in JSON; FastAPI tr? c?ng logical schema. Output t?i thi?u:

~~~json
{
  "query": "authentication flow",
  "database": "data/wifi.duckdb",
  "results": [
    {
      "rank": 1,
      "chunk_id": "?",
      "score": 0.84,
      "content": "?",
      "source_path": "spec.pdf",
      "page_number": 12
    }
  ]
}
~~~

## 8. Phased delivery

1. Refactor skeleton: chuy?n `argparse` wrapper ra `command/`; thay use case placeholder b?ng request/response models thu?n Python.
2. Implement DuckDB schema, document registry v? text/Markdown reader.
3. Implement PDF/DOCX readers v? page-aware chunker.
4. Implement embedding + FAISS build/search.
5. Implement semantic CLI/API query.
6. Add DuckDB FTS + RRF hybrid query.
7. Add tests, benchmark corpus v? documentation.
8. Ch? sau khi ?o nhu c?u m?i c?n nh?c Qdrant, reranker, OCR ho?c image pipeline.

## 9. Khi c?n nh?c Qdrant

Kh?ng d?ng Qdrant ? MVP. ??i sang Qdrant khi c?n concurrent writer/reader, payload filtering ph?c t?p, corpus l?n ho?c hybrid dense+sparse native.

Qdrant s? thay implementation trong `storage/` v? `retrieval/`, c?n CLI, FastAPI v? use case contract gi? nguy?n.
