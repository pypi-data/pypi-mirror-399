# core.py
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer

# Optional: pgvector support with graceful fallback
try:
    import psycopg2
    from pgvector.psycopg2 import register_vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    print("⚠️  pgvector not available - using in-memory storage")

class SemanticDocSearch:
    def __init__(self, context: Dict[str, Any]):
        """Initialize semantic search engine with workflow context"""
        self.context = context
        self.embedding_model = "all-MiniLM-L6-v2"
        self.model = SentenceTransformer(self.embedding_model)
        self.embedding_dimensions = 384  # Fixed for all-MiniLM-L6-v2
        
        # Vector store configuration
        self.use_pgvector = bool(context.get('POSTGRES_URL'))
        self.pg_conn = None
        self.in_memory_store = []
        
        if self.use_pgvector:
            if not PGVECTOR_AVAILABLE:
                raise ImportError("pgvector required for PostgreSQL support. Install with: pip install pgvector psycopg2-binary")
            self._init_pgvector()
        else:
            print("🔄 Using in-memory vector store")
    
    def _init_pgvector(self):
        """Initialize pgvector connection and ensure table exists"""
        try:
            self.pg_conn = psycopg2.connect(self.context['POSTGRES_URL'])
            register_vector(self.pg_conn)
            
            with self.pg_conn.cursor() as cur:
                # Enable pgvector extension
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                
                # Create embeddings table with proper schema
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS doc_embeddings (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        embedding VECTOR(384),
                        source TEXT,
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                self.pg_conn.commit()
            print("🗄️  pgvector initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize pgvector: {e}")
            raise
    
    def _hash_content(self, text: str) -> str:
        """Create SHA-256 hash for content deduplication"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _load_documents(self) -> List[Dict[str, Any]]:
        """Load documents from doc_root directory (supports .txt and .md)"""
        doc_root = self.context.get('doc_root', './docs')
        if not os.path.exists(doc_root):
            print(f"⚠️  doc_root '{doc_root}' does not exist")
            return []
        
        docs = []
        # Support both .txt and .md files
        for file_path in Path(doc_root).glob("*.{txt,md}"):
            try:
                content = file_path.read_text(encoding='utf-8').strip()
                if content:  # Skip empty files
                    docs.append({
                        'id': file_path.name,
                        'content': content,
                        'source': f'file:{file_path.name}'
                    })
                    print(f"📄 Loaded: {file_path.name} ({len(content)} chars)")
                else:
                    print(f"⚠️  Skipping empty file: {file_path.name}")
            except Exception as e:
                print(f"❌ Failed to read {file_path.name}: {e}")
        
        return docs
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks (identical logic to JS version)"""
        if not text or not isinstance(text, str):
            return []
        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if overlap < 0:
            overlap = 0
        if overlap >= chunk_size:
            overlap = chunk_size // 2
        
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += chunk_size - overlap
        
        return chunks
    
    def _validate_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """Validate embedding dimensions and quality"""
        if len(embedding) != self.embedding_dimensions:
            raise ValueError(f"Expected {self.embedding_dimensions}-dim embedding, got {len(embedding)}")
        
        # Check for zero vectors (indicates embedding failure)
        if np.allclose(embedding, 0.0):
            raise ValueError("Zero vector detected - embedding may have failed")
        
        return embedding
    
    def _embed_text(self, text: str) -> np.ndarray:
        """Embed text and validate output"""
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return self._validate_embedding(embedding)
        except Exception as e:
            print(f"❌ Embedding failed for text: {e}")
            raise
    
    def _upsert_to_pgvector(self, doc_id: str, content: str, source: str, embedding: np.ndarray):
        """Upsert document embedding to pgvector"""
        if not self.pg_conn:
            return
        
        try:
            with self.pg_conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO doc_embeddings (id, content, embedding, source) 
                       VALUES (%s, %s, %s, %s) 
                       ON CONFLICT (id) 
                       DO UPDATE SET embedding = EXCLUDED.embedding, content = EXCLUDED.content""",
                    (doc_id, content, embedding.tolist(), source)
                )
                self.pg_conn.commit()
                print(f"✅ Upserted to pgvector: {doc_id}")
        except Exception as e:
            print(f"❌ pgvector upsert failed: {e}")
            raise
    
    def _upsert_to_memory(self, doc_id: str, content: str, source: str, embedding: np.ndarray):
        """Store document embedding in memory"""
        self.in_memory_store.append({
            'id': doc_id,
            'content': content,
            'embedding': embedding,
            'source': source
        })
        print(f"✅ Upserted to memory: {doc_id}")
    
    def _search_pgvector(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in pgvector"""
        if not self.pg_conn:
            return []
        
        try:
            with self.pg_conn.cursor() as cur:
                cur.execute(
                    """SELECT id, content, source, embedding <-> %s AS distance 
                       FROM doc_embeddings 
                       ORDER BY distance 
                       LIMIT %s""",
                    (query_embedding.tolist(), top_k)
                )
                results = cur.fetchall()
                return [
                    {
                        'id': r[0],
                        'content': r[1],
                        'source': r[2],
                        'score': 1.0 - float(r[3])  # Convert distance to cosine similarity
                    }
                    for r in results
                ]
        except Exception as e:
            print(f"❌ pgvector search failed: {e}")
            return []
    
    def _search_memory(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in memory using cosine similarity"""
        if not self.in_memory_store:
            return []
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = []
            
            for doc in self.in_memory_store:
                sim = cosine_similarity([query_embedding], [doc['embedding']])[0][0]
                similarities.append((sim, doc))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            return [
                {
                    'id': doc['id'],
                    'content': doc['content'],
                    'source': doc['source'],
                    'score': float(similarity)
                }
                for similarity, doc in similarities[:top_k]
            ]
        except Exception as e:
            print(f"❌ In-memory search failed: {e}")
            return []
    
    def _format_results(self, matches: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Format results to match O-lang JS resolver output exactly"""
        text = "\n\n".join([match['content'] for match in matches]) if matches else ""
        
        return {
            "query": query,
            "text": text,
            "matches": matches
        }
    
    def handle_action(self, action: str) -> Dict[str, Any]:
        """Handle 'Ask doc-search "query"' action with full error handling"""
        # Extract query from action string (identical to JS logic)
        if not action.startswith("Ask doc-search"):
            raise ValueError(f"Invalid action: {action}")
        
        # Extract query text between quotes
        if '"' in action:
            query = action.split('"')[1]
        else:
            # Fallback: get last part after "Ask doc-search"
            query = action.split(" ", 2)[-1] if len(action.split(" ", 2)) > 2 else ""
        
        if not query.strip():
            return self._format_results([], query)
        
        print(f"🔍 Processing query: '{query}'")
        
        # Load and process documents
        documents = self._load_documents()
        print(f"🔄 Ingesting {len(documents)} documents")
        
        for doc in documents:
            chunks = self._chunk_text(doc['content'], 500, 50) or [doc['content']]
            
            for i, chunk_text in enumerate(chunks):
                if not chunk_text.strip():
                    continue
                
                try:
                    embedding = self._embed_text(chunk_text)
                    doc_id = f"{doc['id']}:{i}"
                    
                    if self.use_pgvector:
                        self._upsert_to_pgvector(doc_id, chunk_text, doc['source'], embedding)
                    else:
                        self._upsert_to_memory(doc_id, chunk_text, doc['source'], embedding)
                        
                except Exception as e:
                    print(f"⚠️  Failed to process chunk {doc_id}: {e}")
                    continue
        
        # Perform semantic search
        try:
            query_embedding = self._embed_text(query)
            
            if self.use_pgvector:
                matches = self._search_pgvector(query_embedding)
            else:
                matches = self._search_memory(query_embedding)
            
            result = self._format_results(matches, query)
            print(f"📊 Found {len(matches)} matches")
            if matches:
                print(f"🎯 Top match score: {matches[0]['score']:.4f}")
            
            return result
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return self._format_results([], query)