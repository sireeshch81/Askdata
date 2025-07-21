# ChromaDB Vector Database Service

This service provides vector database functionality for storing and retrieving embeddings of natural language questions and SQL queries.

## Overview

The ChromaDB service is responsible for:

- Storing embeddings of natural language questions and their corresponding SQL queries
- Retrieving similar questions and queries for RAG functionality
- Storing database schema information for context enhancement

## Collections

- `nlp_sql_pairs` - Stores natural language questions and their SQL query pairs
- `schema_info` - Stores database schema information


