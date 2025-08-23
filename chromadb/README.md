# ChromaDB Vector Database Service (FastAPI)

This service is a FastAPI microservice that embeds natural language text using a SentenceTransformer model and persists vectors and documents into a local ChromaDB database.

## Overview

Responsibilities:
- Accept text from upstream services, embed it, and store text + vector + metadata in ChromaDB
- Query the vector database by text (embedding under the hood)
- Provide basic health and collection listing endpoints

ChromaDB persistence lives under `./chromadb/chroma_data` and is mounted as `/data` inside the container.

The service will be available at `http://localhost:9000`.

## Endpoints

- GET /health
  - Returns `{ "status": "ok" }` if the service is up.

- GET /collections
  - Returns available collection names: `{ "collections": ["nlp_sql_pairs", ...] }`.

- POST /embed-and-store
  - Body:
    ```json
    {
      "text": "What is our total revenue?",
      "id": "optional-custom-id",
      "metadata": {"source": "api"},
      "collection": "nlp_sql_pairs"
    }
    ```
  - Response includes the record id, collection and embedding dimension.

- POST /query
  - Body:
    ```json
    {
      "query_text": "total revenue",
      "top_k": 5,
      "collection": "nlp_sql_pairs"
    }
    ```
  - Returns top-k nearest neighbors with ids, distances, metadata and documents.


## Environment Variables

- `PERSIST_DIRECTORY` (default `/data`) – where ChromaDB stores data.
- `DEFAULT_COLLECTION` (default `nlp_sql_pairs`) – collection used when not provided in requests.
- `EMBEDDING_MODEL` (default `sentence-transformers/all-MiniLM-L6-v2`) – Sentence Transformer model to use.
- `ANONYMIZED_TELEMETRY` (default `FALSE`) – disable Chroma telemetry.

## Notes

- On first run the model will be downloaded into the container cache (`/cache`).
- If you want to pre-pull models or control cache persistence, you can mount an external volume to `/cache` similarly to `/data`.


