from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import os
import uuid

import chromadb
from chromadb.config import Settings

from sentence_transformers import SentenceTransformer


# Environment configuration
PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY", "/data")
ANONYMIZED_TELEMETRY = os.getenv("ANONYMIZED_TELEMETRY", "FALSE").upper() == "TRUE"
DEFAULT_COLLECTION = os.getenv("DEFAULT_COLLECTION", "nlp_sql_pairs")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Ensure directories exist
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

# Initialize FastAPI
app = FastAPI(title="ChromaDB Vector Service", version="0.1.0")


class EmbedStoreRequest(BaseModel):
    text: str = Field(..., description="Natural language text to embed and store")
    id: Optional[str] = Field(None, description="Optional custom id for the record")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    collection: Optional[str] = Field(None, description="Collection name; defaults to env DEFAULT_COLLECTION")


class QueryRequest(BaseModel):
    query_text: str = Field(..., description="Natural language text to embed and query")
    top_k: int = Field(5, ge=1, le=50)
    collection: Optional[str] = Field(None)


# Lazy singletons
_chroma_client = None
_embedder: Optional[SentenceTransformer] = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        # Allow cache dirs to be configured (useful in container)
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", "/cache/sentence-transformers")
        os.makedirs(os.environ["SENTENCE_TRANSFORMERS_HOME"], exist_ok=True)
        os.environ.setdefault("HUGGINGFACE_HUB_CACHE", "/cache/huggingface")
        os.makedirs(os.environ["HUGGINGFACE_HUB_CACHE"], exist_ok=True)
        _embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedder


def get_chroma():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=ANONYMIZED_TELEMETRY)
        )
    return _chroma_client


def get_or_create_collection(name: str):
    client = get_chroma()
    return client.get_or_create_collection(name=name)


@app.get("/health")
async def health() -> Dict[str, str]:
    # simple check that storage path is writable and model can be referenced
    try:
        os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
        # Don't load model on health, just check env values exist
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/collections")
async def list_collections() -> Dict[str, List[str]]:
    client = get_chroma()
    names = [c.name for c in client.list_collections()]
    return {"collections": names}


@app.post("/embed-and-store")
async def embed_and_store(req: EmbedStoreRequest) -> Dict[str, Any]:
    collection_name = req.collection or DEFAULT_COLLECTION
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text must be non-empty")

    embedder = get_embedder()
    embedding = embedder.encode([req.text], convert_to_numpy=True)[0]

    col = get_or_create_collection(collection_name)
    record_id = req.id or str(uuid.uuid4())

    metadata = req.metadata or {}
    metadata.setdefault("source", "api")

    col.upsert(
        ids=[record_id],
        embeddings=[embedding.tolist()],
        documents=[req.text],
        metadatas=[metadata],
    )

    return {
        "id": record_id,
        "collection": collection_name,
        "embedding_dim": len(embedding),
        "metadata": metadata,
    }


@app.post("/query")
async def query(req: QueryRequest) -> Dict[str, Any]:
    collection_name = req.collection or DEFAULT_COLLECTION

    embedder = get_embedder()
    query_vec = embedder.encode([req.query_text], convert_to_numpy=True)[0].tolist()

    col = get_or_create_collection(collection_name)

    results = col.query(
        query_embeddings=[query_vec],
        n_results=req.top_k,
        include=["distances", "metadatas", "documents", "embeddings", "ids"],
    )

    # Flatten single-query outputs
    out = []
    for i in range(len(results.get("ids", [[]])[0])):
        out.append({
            "id": results["ids"][0][i],
            "distance": results.get("distances", [[None]])[0][i],
            "metadata": results.get("metadatas", [[None]])[0][i],
            "document": results.get("documents", [[None]])[0][i],
        })

    return {
        "collection": collection_name,
        "query": req.query_text,
        "results": out,
    }
