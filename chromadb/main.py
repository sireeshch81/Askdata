from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import os
import uuid
import json
import logging
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings
# Set cache directories before importing sentence-transformers
import os
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", "/cache/sentence-transformers")  
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", "/cache/huggingface")
os.makedirs(os.environ["SENTENCE_TRANSFORMERS_HOME"], exist_ok=True)
os.makedirs(os.environ["HUGGINGFACE_HUB_CACHE"], exist_ok=True)

from sentence_transformers import SentenceTransformer


# Database imports
import pymysql
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY", "/data")
ANONYMIZED_TELEMETRY = os.getenv("ANONYMIZED_TELEMETRY", "FALSE").upper() == "TRUE"
DEFAULT_COLLECTION = os.getenv("DEFAULT_COLLECTION", "nlp_sql_pairs")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Database configuration - using Docker service names
OLTP_DATABASE_URL = f"mysql+pymysql://{os.getenv('MYSQL_OLTP_USER', 'askdata_user')}:{os.getenv('MYSQL_OLTP_PASSWORD', 'askdata_password')}@{os.getenv('MYSQL_OLTP_HOST', 'oltp-db')}:{os.getenv('MYSQL_OLTP_PORT', '3306')}/{os.getenv('MYSQL_OLTP_DATABASE', 'askdata_oltp')}"

DW_DATABASE_URL = f"mysql+pymysql://{os.getenv('MYSQL_DW_USER', 'askdata_dw_user')}:{os.getenv('MYSQL_DW_PASSWORD', 'askdata_dw_password')}@{os.getenv('MYSQL_DW_HOST', 'dw-db')}:{os.getenv('MYSQL_DW_PORT', '3306')}/{os.getenv('MYSQL_DW_DATABASE', 'askdata_dw')}"

# Ensure directories exist
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

# Initialize FastAPI
app = FastAPI(title="ChromaDB Vector Service with Metadata Integration", version="0.2.0")

# Existing Models
class EmbedStoreRequest(BaseModel):
    text: str = Field(..., description="Natural language text to embed and store")
    id: Optional[str] = Field(None, description="Optional custom id for the record")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    collection: Optional[str] = Field(None, description="Collection name; defaults to env DEFAULT_COLLECTION")

class QueryRequest(BaseModel):
    query_text: str = Field(..., description="Natural language text to embed and query")
    top_k: int = Field(5, ge=1, le=50)
    collection: Optional[str] = Field(None)

# New Models for Metadata Integration
class SchemaLoadRequest(BaseModel):
    database_type: str = Field(..., description="Database type: 'oltp' or 'dw'")
    collection: Optional[str] = Field("database_metadata", description="Collection for metadata storage")

class TableSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language description of needed tables")
    database_type: Optional[str] = Field(None, description="Filter by database type: 'oltp' or 'dw'")
    top_k: int = Field(5, ge=1, le=20)
    collection: Optional[str] = Field("database_metadata")

class SQLContextRequest(BaseModel):
    user_query: str = Field(..., description="User's natural language query")
    max_tables: int = Field(5, ge=1, le=10, description="Maximum number of relevant tables to include")
    include_relationships: bool = Field(True, description="Include foreign key relationships")
    collection: Optional[str] = Field("database_metadata")

# Data Classes
@dataclass
class TableMetadata:
    database_name: str
    table_name: str
    table_type: str  # 'oltp' or 'dw'
    table_comment: str
    columns: List[Dict[str, Any]]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    indexes: List[Dict[str, Any]]
    row_count: Optional[int] = None
    
    def to_searchable_document(self) -> str:
        """Convert metadata to searchable document format"""
        doc_parts = [
            f"Database: {self.database_name} ({self.table_type.upper()})",
            f"Table: {self.table_name}",
        ]
        
        if self.table_comment:
            doc_parts.append(f"Description: {self.table_comment}")
        
        # Business context based on table naming patterns
        business_context = self._generate_business_context()
        if business_context:
            doc_parts.append(f"Business Context: {business_context}")
            
        # Add column information
        doc_parts.append("Columns:")
        for col in self.columns[:10]:  # Limit to first 10 columns for readability
            col_info = f"  - {col['name']} ({col['type']}"
            if col.get('nullable') == 'NO':
                col_info += ", NOT NULL"
            if col.get('comment'):
                col_info += f") - {col['comment']}"
            else:
                col_info += ")"
            doc_parts.append(col_info)
        
        if len(self.columns) > 10:
            doc_parts.append(f"  ... and {len(self.columns) - 10} more columns")
        
        # Add key information
        if self.primary_keys:
            doc_parts.append(f"Primary Keys: {', '.join(self.primary_keys)}")
            
        if self.foreign_keys:
            fk_info = []
            for fk in self.foreign_keys:
                fk_info.append(f"{fk['column']} -> {fk['referenced_table']}.{fk['referenced_column']}")
            doc_parts.append(f"Foreign Keys: {'; '.join(fk_info)}")
        
        if self.row_count is not None:
            doc_parts.append(f"Approximate Rows: {self.row_count:,}")
            
        return "\n".join(doc_parts)
    
    def _generate_business_context(self) -> str:
        """Generate business context based on table and column names"""
        table_lower = self.table_name.lower()
        contexts = []
        
        # Table-level context
        if 'member' in table_lower:
            contexts.append("Customer/member information")
        elif 'payment' in table_lower:
            contexts.append("Payment transactions and history")
        elif 'credit_card' in table_lower or 'card' in table_lower:
            contexts.append("Credit card details and management")
        elif 'financial_health' in table_lower or 'health' in table_lower:
            contexts.append("Financial health metrics and scoring")
        elif 'product' in table_lower:
            contexts.append("Financial products and offerings")
        elif 'recommendation' in table_lower:
            contexts.append("Product recommendations and suggestions")
        elif table_lower.startswith('dim_'):
            contexts.append("Dimension table for analytics")
        elif table_lower.startswith('fact_'):
            contexts.append("Fact table for metrics and measures")
        
        # Column-level context
        column_names = [col['name'].lower() for col in self.columns]
        if any('income' in col for col in column_names):
            contexts.append("Income-related data")
        if any('score' in col for col in column_names):
            contexts.append("Scoring and rating metrics")
        if any('balance' in col for col in column_names):
            contexts.append("Account balances and amounts")
        if any('date' in col or 'time' in col for col in column_names):
            contexts.append("Time-series data")
            
        return "; ".join(contexts)

# Lazy singletons
_chroma_client = None
_embedder: Optional[SentenceTransformer] = None
_oltp_engine = None
_dw_engine = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        # Environment variables already set at module level
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

def get_database_engine(database_type: str):
    """Get database engine for specified type"""
    global _oltp_engine, _dw_engine
    
    if database_type == 'oltp':
        if _oltp_engine is None:
            _oltp_engine = create_engine(OLTP_DATABASE_URL, pool_pre_ping=True)
        return _oltp_engine
    elif database_type == 'dw':
        if _dw_engine is None:
            _dw_engine = create_engine(DW_DATABASE_URL, pool_pre_ping=True)
        return _dw_engine
    else:
        raise ValueError(f"Invalid database_type: {database_type}. Must be 'oltp' or 'dw'")

def get_or_create_collection(name: str):
    client = get_chroma()
    return client.get_or_create_collection(name=name)

# Database Schema Extraction
class SchemaExtractor:
    """Extract schema metadata from MySQL databases"""
    
    @staticmethod
    def extract_table_metadata(engine, database_name: str, database_type: str) -> List[TableMetadata]:
        """Extract metadata for all tables in a database"""
        tables_metadata = []
        
        with engine.connect() as conn:
            # Get all tables
            tables_result = conn.execute(text("""
                SELECT TABLE_NAME, TABLE_COMMENT, TABLE_ROWS
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = :db_name AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """), {"db_name": database_name})
            
            tables = tables_result.fetchall()
            logger.info(f"Found {len(tables)} tables in {database_name}")
            
            for table in tables:
                table_name = table[0]
                table_comment = table[1] or ""
                row_count = table[2]
                
                try:
                    # Extract column information
                    columns = SchemaExtractor._extract_columns(conn, database_name, table_name)
                    primary_keys = SchemaExtractor._extract_primary_keys(conn, database_name, table_name)
                    foreign_keys = SchemaExtractor._extract_foreign_keys(conn, database_name, table_name)
                    indexes = SchemaExtractor._extract_indexes(conn, database_name, table_name)
                    
                    metadata = TableMetadata(
                        database_name=database_name,
                        table_name=table_name,
                        table_type=database_type,
                        table_comment=table_comment,
                        columns=columns,
                        primary_keys=primary_keys,
                        foreign_keys=foreign_keys,
                        indexes=indexes,
                        row_count=row_count
                    )
                    
                    tables_metadata.append(metadata)
                    
                except Exception as e:
                    logger.error(f"Error processing table {table_name}: {e}")
                    continue
        
        return tables_metadata
    
    @staticmethod
    def _extract_columns(conn, database_name: str, table_name: str) -> List[Dict[str, Any]]:
        """Extract column information"""
        columns_result = conn.execute(text("""
            SELECT 
                COLUMN_NAME as name,
                DATA_TYPE as data_type,
                COLUMN_TYPE as full_type,
                IS_NULLABLE as nullable,
                COLUMN_DEFAULT as default_value,
                CHARACTER_MAXIMUM_LENGTH as max_length,
                NUMERIC_PRECISION as `precision`,
                NUMERIC_SCALE as `scale`,
                COLUMN_COMMENT as comment,
                COLUMN_KEY as key_type
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = :db_name AND TABLE_NAME = :table_name
            ORDER BY ORDINAL_POSITION
        """), {"db_name": database_name, "table_name": table_name})
        
        columns = []
        for col in columns_result.fetchall():
            column_info = {
                'name': col[0],
                'data_type': col[1],
                'type': col[2],  # Full type with length/precision
                'nullable': col[3],
                'default': col[4],
                'max_length': col[5],
                'precision': col[6],
                'scale': col[7],
                'comment': col[8] or "",
                'key_type': col[9] or ""
            }
            columns.append(column_info)
        
        return columns
    
    @staticmethod
    def _extract_primary_keys(conn, database_name: str, table_name: str) -> List[str]:
        """Extract primary key columns"""
        pk_result = conn.execute(text("""
            SELECT COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = :db_name 
                AND TABLE_NAME = :table_name 
                AND CONSTRAINT_NAME = 'PRIMARY'
            ORDER BY ORDINAL_POSITION
        """), {"db_name": database_name, "table_name": table_name})
        
        return [row[0] for row in pk_result.fetchall()]
    
    @staticmethod
    def _extract_foreign_keys(conn, database_name: str, table_name: str) -> List[Dict[str, str]]:
        """Extract foreign key relationships"""
        fk_result = conn.execute(text("""
            SELECT 
                COLUMN_NAME as column_name,
                REFERENCED_TABLE_NAME as referenced_table,
                REFERENCED_COLUMN_NAME as referenced_column,
                CONSTRAINT_NAME as constraint_name
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = :db_name 
                AND TABLE_NAME = :table_name 
                AND REFERENCED_TABLE_NAME IS NOT NULL
        """), {"db_name": database_name, "table_name": table_name})
        
        foreign_keys = []
        for fk in fk_result.fetchall():
            foreign_keys.append({
                'column': fk[0],
                'referenced_table': fk[1],
                'referenced_column': fk[2],
                'constraint_name': fk[3]
            })
        
        return foreign_keys
    
    @staticmethod
    def _extract_indexes(conn, database_name: str, table_name: str) -> List[Dict[str, Any]]:
        """Extract index information"""
        try:
            idx_result = conn.execute(text(f"SHOW INDEX FROM `{table_name}` FROM `{database_name}`"))
            
            indexes = []
            for idx in idx_result.fetchall():
                indexes.append({
                    'name': idx[2],  # Key_name
                    'column': idx[4],  # Column_name
                    'unique': not bool(idx[1]),  # Non_unique (inverted)
                    'sequence': idx[3]  # Seq_in_index
                })
            
            return indexes
        except Exception as e:
            logger.warning(f"Could not extract indexes for {table_name}: {e}")
            return []

# Existing endpoints (unchanged)
@app.get("/health")
async def health() -> Dict[str, str]:
    try:
        os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
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

# New Metadata Integration Endpoints

@app.post("/load-database-schema")
async def load_database_schema(req: SchemaLoadRequest) -> Dict[str, Any]:
    """Extract and load database schema metadata into ChromaDB"""
    
    if req.database_type not in ['oltp', 'dw']:
        raise HTTPException(status_code=400, detail="database_type must be 'oltp' or 'dw'")
    
    try:
        # Get database engine and info
        engine = get_database_engine(req.database_type)
        database_name = os.getenv(f'MYSQL_{req.database_type.upper()}_DATABASE')
        
        logger.info(f"Extracting schema metadata from {database_name} ({req.database_type})")
        
        # Extract schema metadata
        tables_metadata = SchemaExtractor.extract_table_metadata(engine, database_name, req.database_type)
        
        # Get ChromaDB collection
        collection = get_or_create_collection(req.collection)
        embedder = get_embedder()
        
        # Clear existing metadata for this database type
        try:
            existing_results = collection.get(where={"database_type": req.database_type})
            if existing_results['ids']:
                collection.delete(ids=existing_results['ids'])
                logger.info(f"Cleared {len(existing_results['ids'])} existing records for {req.database_type}")
        except Exception as e:
            logger.warning(f"Could not clear existing records: {e}")
        
        # Store each table's metadata
        stored_count = 0
        for table_meta in tables_metadata:
            try:
                # Convert to searchable document
                document = table_meta.to_searchable_document()
                
                # Create embedding
                embedding = embedder.encode([document], convert_to_numpy=True)[0]
                
                # Create metadata for ChromaDB
                chroma_metadata = {
                    "database_name": table_meta.database_name,
                    "table_name": table_meta.table_name,
                    "database_type": table_meta.table_type,
                    "row_count": table_meta.row_count or 0,
                    "column_count": len(table_meta.columns),
                    "has_primary_key": len(table_meta.primary_keys) > 0,
                    "has_foreign_keys": len(table_meta.foreign_keys) > 0,
                    "source": "schema_extraction"
                }
                
                # Create unique ID
                record_id = f"{table_meta.database_name}_{table_meta.table_name}"
                
                # Store in ChromaDB
                collection.upsert(
                    ids=[record_id],
                    embeddings=[embedding.tolist()],
                    documents=[document],
                    metadatas=[chroma_metadata]
                )
                
                stored_count += 1
                logger.debug(f"Stored metadata for {table_meta.table_name}")
                
            except Exception as e:
                logger.error(f"Error storing metadata for {table_meta.table_name}: {e}")
                continue
        
        return {
            "success": True,
            "database_type": req.database_type,
            "database_name": database_name,
            "tables_processed": len(tables_metadata),
            "tables_stored": stored_count,
            "collection": req.collection
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading schema: {str(e)}")

@app.post("/load-business-schema")
async def load_business_schema(collection: str = "database_metadata") -> Dict[str, Any]:
    """Load business schema descriptions from schema_description.txt"""
    
    try:
        # Read schema description file (if it exists in the container)
        schema_file_path = "/app/schema_description.txt"
        if not os.path.exists(schema_file_path):
            raise HTTPException(status_code=404, detail="schema_description.txt not found in container")
        
        with open(schema_file_path, 'r') as f:
            schema_content = f.read()
        
        # Parse the content into sections (basic parsing)
        sections = schema_content.split('-- =============================================================================')
        
        embedder = get_embedder()
        col = get_or_create_collection(collection)
        
        # Clear existing business schema records
        try:
            existing = col.get(where={"source": "business_schema"})
            if existing['ids']:
                col.delete(ids=existing['ids'])
                logger.info(f"Cleared {len(existing['ids'])} existing business schema records")
        except Exception as e:
            logger.warning(f"Could not clear existing business schema records: {e}")
        
        stored_count = 0
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            if section.strip():
                # Extract table name from section header
                lines = section.strip().split('\n')
                table_name = "unknown"
                for line in lines[:5]:  # Check first few lines
                    if 'TABLE' in line and 'CREATE' in line:
                        # Extract table name from CREATE TABLE statement
                        parts = line.split()
                        for j, part in enumerate(parts):
                            if part.upper() == 'TABLE' and j + 1 < len(parts):
                                table_name = parts[j + 1].strip('(')
                                break
                        break
                
                # Create document
                document = f"Business Schema Definition - {table_name}\n\n{section.strip()}"
                
                # Create embedding
                embedding = embedder.encode([document], convert_to_numpy=True)[0]
                
                # Metadata
                metadata = {
                    "table_name": table_name,
                    "source": "business_schema",
                    "section_number": i,
                    "document_type": "schema_definition"
                }
                
                # Store
                record_id = f"business_schema_{table_name}_{i}"
                col.upsert(
                    ids=[record_id],
                    embeddings=[embedding.tolist()],
                    documents=[document],
                    metadatas=[metadata]
                )
                
                stored_count += 1
        
        return {
            "success": True,
            "sections_processed": len(sections) - 1,
            "sections_stored": stored_count,
            "collection": collection,
            "source": "schema_description.txt"
        }
        
    except Exception as e:
        logger.error(f"Error loading business schema: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading business schema: {str(e)}")

@app.post("/search-tables")
async def search_tables(req: TableSearchRequest) -> Dict[str, Any]:
    """Search for relevant tables based on natural language query"""
    
    try:
        embedder = get_embedder()
        col = get_or_create_collection(req.collection)
        
        # Create query embedding
        query_embedding = embedder.encode([req.query], convert_to_numpy=True)[0].tolist()
        
        # Build where clause
        where_clause = {}
        if req.database_type:
            where_clause["database_type"] = req.database_type
        
        # Search
        results = col.query(
            query_embeddings=[query_embedding],
            n_results=req.top_k,
            where=where_clause if where_clause else None,
            include=["distances", "metadatas", "documents"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results.get("ids", [[]])[0])):
            result = {
                "id": results["ids"][0][i],
                "table_name": results["metadatas"][0][i].get("table_name", "unknown"),
                "database_name": results["metadatas"][0][i].get("database_name", "unknown"),
                "database_type": results["metadatas"][0][i].get("database_type", "unknown"),
                "relevance_score": 1 - (results["distances"][0][i] if results.get("distances") else 0),
                "row_count": results["metadatas"][0][i].get("row_count", 0),
                "column_count": results["metadatas"][0][i].get("column_count", 0),
                "metadata": results["metadatas"][0][i],
                "schema_info": results["documents"][0][i]
            }
            formatted_results.append(result)
        
        return {
            "query": req.query,
            "database_type": req.database_type,
            "results_count": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        logger.error(f"Error searching tables: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching tables: {str(e)}")

@app.post("/generate-sql-context")
async def generate_sql_context(req: SQLContextRequest) -> Dict[str, Any]:
    """Generate comprehensive context for LLM SQL generation"""
    
    try:
        # Search for relevant tables
        search_req = TableSearchRequest(
            query=req.user_query,
            top_k=req.max_tables,
            collection=req.collection
        )
        
        search_results = await search_tables(search_req)
        
        # Build comprehensive context
        context = {
            "user_query": req.user_query,
            "relevant_tables": search_results["results"],
            "context_summary": _build_context_summary(search_results["results"]),
            "suggested_relationships": [],
            "llm_prompt": _build_llm_prompt(req.user_query, search_results["results"], req.include_relationships)
        }
        
        # Add relationship suggestions if requested
        if req.include_relationships:
            context["suggested_relationships"] = _extract_relationships(search_results["results"])
        
        return context
        
    except Exception as e:
        logger.error(f"Error generating SQL context: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating SQL context: {str(e)}")

def _build_context_summary(results: List[Dict]) -> Dict[str, Any]:
    """Build a summary of the context"""
    oltp_tables = [r for r in results if r["database_type"] == "oltp"]
    dw_tables = [r for r in results if r["database_type"] == "dw"]
    
    return {
        "total_tables": len(results),
        "oltp_tables": len(oltp_tables),
        "dw_tables": len(dw_tables),
        "primary_database_type": "dw" if len(dw_tables) > len(oltp_tables) else "oltp",
        "table_names": [r["table_name"] for r in results],
        "total_approximate_rows": sum(r.get("row_count", 0) for r in results)
    }

def _extract_relationships(results: List[Dict]) -> List[Dict[str, str]]:
    """Extract potential relationships from table metadata"""
    relationships = []
    
    for result in results:
        schema_info = result.get("schema_info", "")
        if "Foreign Keys:" in schema_info:
            # Parse foreign key information from schema
            lines = schema_info.split('\n')
            for line in lines:
                if line.startswith("Foreign Keys:"):
                    fk_info = line.replace("Foreign Keys:", "").strip()
                    if fk_info:
                        relationships.append({
                            "from_table": result["table_name"],
                            "relationship": fk_info,
                            "database_type": result["database_type"]
                        })
    
    return relationships

def _build_llm_prompt(user_query: str, results: List[Dict], include_relationships: bool) -> str:
    """Build a comprehensive LLM prompt for SQL generation"""
    
    # Determine primary database type
    dw_count = sum(1 for r in results if r["database_type"] == "dw")
    oltp_count = len(results) - dw_count
    primary_db_type = "Data Warehouse (Analytics)" if dw_count > oltp_count else "OLTP (Transactional)"
    
    prompt_parts = [
        "# SQL Query Generation Task",
        f"Generate a SQL query for: **{user_query}**",
        "",
        f"**Primary Database Type:** {primary_db_type}",
        "",
        "## Available Tables and Schema Information:",
        ""
    ]
    
    # Add table information
    for i, result in enumerate(results, 1):
        relevance_pct = f"{result.get('relevance_score', 0) * 100:.1f}%"
        prompt_parts.extend([
            f"### {i}. {result['database_name']}.{result['table_name']} ({result['database_type'].upper()}) - Relevance: {relevance_pct}",
            f"**Rows:** {result.get('row_count', 0):,} | **Columns:** {result.get('column_count', 0)}",
            "",
            "```sql",
            result.get('schema_info', 'No schema information available'),
            "```",
            ""
        ])
    
    # Add relationship information
    if include_relationships:
        relationships = _extract_relationships(results)
        if relationships:
            prompt_parts.extend([
                "## Table Relationships:",
                ""
            ])
            for rel in relationships:
                prompt_parts.append(f"- **{rel['from_table']}**: {rel['relationship']}")
            prompt_parts.append("")
    
    # Add guidelines
    prompt_parts.extend([
        "## SQL Generation Guidelines:",
        "- Use appropriate JOINs based on foreign key relationships shown above",
        "- Include meaningful column aliases for readability",
        "- Add appropriate WHERE clauses for filtering",
        "- Use aggregate functions (COUNT, SUM, AVG) when appropriate for analytical queries",
        "- For date ranges, use proper date functions and formatting",
        "- Consider adding LIMIT clauses for large result sets",
        "- For Data Warehouse queries, leverage dimension and fact table structure",
        "- For OLTP queries, focus on transactional patterns and real-time data",
        "",
        "## Expected Output Format:",
        "```sql",
        "-- Your optimized SQL query here",
        "-- Include comments explaining key joins and logic",
        "```",
        "",
        "**Explanation:** Brief description of the query approach, table choices, and key business logic."
    ])
    
    return '\n'.join(prompt_parts)

# Health check for database connections
@app.get("/health/databases")
async def health_databases() -> Dict[str, Any]:
    """Check health of database connections"""
    health_status = {
        "oltp": {"status": "unknown", "error": None},
        "dw": {"status": "unknown", "error": None}
    }
    
    # Test OLTP connection
    try:
        engine = get_database_engine('oltp')
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            health_status["oltp"]["status"] = "healthy" if result == 1 else "error"
    except Exception as e:
        health_status["oltp"]["status"] = "error"
        health_status["oltp"]["error"] = str(e)
    
    # Test DW connection
    try:
        engine = get_database_engine('dw')
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            health_status["dw"]["status"] = "healthy" if result == 1 else "error"
    except Exception as e:
        health_status["dw"]["status"] = "error"
        health_status["dw"]["error"] = str(e)
    
    overall_status = "healthy" if all(db["status"] == "healthy" for db in health_status.values()) else "degraded"
    
    return {
        "overall_status": overall_status,
        "databases": health_status,
        "timestamp": "now"  # You could use actual timestamp here
    }
