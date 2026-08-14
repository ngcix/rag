"""FastAPI routes that delegate to shared RAG use cases."""

from fastapi import FastAPI, HTTPException

from rag.api.schemas import CollectionResponse, IngestRequest, QueryRequest, QueryResponse
from rag.use_cases.ingest import ingest
from rag.use_cases.inspect import inspect_collection
from rag.use_cases.query import query

app = FastAPI(title="RAG", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest", status_code=202)
def ingest_documents(request: IngestRequest) -> dict[str, str]:
    try:
        ingest(request.source, collection=request.collection, replace=request.replace)
    except NotImplementedError as error:
        raise HTTPException(status_code=501, detail=str(error)) from error
    return {"status": "accepted"}


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest) -> QueryResponse:
    try:
        results = query(request.text, collection=request.collection, top_k=request.top_k, hybrid=request.hybrid)
    except NotImplementedError as error:
        raise HTTPException(status_code=501, detail=str(error)) from error
    return QueryResponse(results=results)


@app.get("/collections/{collection}", response_model=CollectionResponse)
def get_collection(collection: str) -> CollectionResponse:
    try:
        details = inspect_collection(collection)
    except NotImplementedError as error:
        raise HTTPException(status_code=501, detail=str(error)) from error
    return CollectionResponse(collection=collection, details=details)
