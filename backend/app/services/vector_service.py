"""
Vector Service - PostgreSQL + pgvector implementation
Handles document storage, embedding, and similarity search.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
import logging

from app.models import Document
from app.database import SessionLocal
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class VectorService:
    """
    Manages vector embeddings in PostgreSQL with pgvector.
    Provides persistent storage and cosine similarity search.
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        logger.info("✅ VectorService initialized with pgvector backend")
    
    def add_documents(
        self, 
        texts: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[int]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text chunks to embed and store
            metadatas: Optional list of metadata dicts for each text
        
        Returns:
            List of document IDs
        """
        if not texts:
            logger.warning("⚠️ No texts provided to add_documents")
            return []
        
        # Generate embeddings
        embeddings = self.embedding_service.embed_documents(texts)
        
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        # Store in database
        db = SessionLocal()
        doc_ids = []
        
        try:
            for text, embedding, metadata in zip(texts, embeddings, metadatas):
                doc = Document(
                    content=text,
                    embedding=embedding,
                    document_metadata=metadata
                )
                db.add(doc)
                db.flush()  # Get the ID
                doc_ids.append(doc.id)
            
            db.commit()
            logger.info(f"✅ Added {len(doc_ids)} documents to vector store")
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to add documents: {e}")
            raise
        finally:
            db.close()
        
        return doc_ids
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query: Query text
            k: Number of results to return
            filter_metadata: Optional metadata filters (not implemented yet)
        
        Returns:
            List of dicts with 'content', 'metadata', and 'score'
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)
        
        db = SessionLocal()
        
        try:
            # pgvector cosine distance query
            # Using <=> operator for cosine distance (1 - cosine_similarity)
            # Convert embedding list to string format that pgvector accepts
            embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
            
            sql = text("""
                SELECT 
                    id,
                    content,
                    document_metadata,
                    1 - (embedding <=> CAST(:query_embedding as vector)) as similarity
                FROM documents
                ORDER BY embedding <=> CAST(:query_embedding as vector)
                LIMIT :k
            """)
            
            result = db.execute(
                sql,
                {
                    "query_embedding": embedding_str,
                    "k": k
                }
            )
            
            documents = []
            for row in result:
                documents.append({
                    "id": row.id,
                    "content": row.content,
                    "metadata": row.document_metadata or {},
                    "score": float(row.similarity)
                })
            
            logger.info(f"🔍 Found {len(documents)} similar documents for query")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Similarity search failed: {e}")
            raise
        finally:
            db.close()
    
    def clear_all(self) -> int:
        """
        Clear all documents from the vector store.
        
        Returns:
            Number of documents deleted
        """
        db = SessionLocal()
        
        try:
            count = db.query(Document).count()
            db.query(Document).delete()
            db.commit()
            logger.info(f"🗑️ Cleared {count} documents from vector store")
            return count
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to clear vector store: {e}")
            raise
        finally:
            db.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dict with document count and other stats
        """
        db = SessionLocal()
        
        try:
            count = db.query(Document).count()
            
            # Get oldest and newest documents
            oldest = db.query(Document).order_by(Document.created_at.asc()).first()
            newest = db.query(Document).order_by(Document.created_at.desc()).first()
            
            stats = {
                "document_count": count,
                "oldest_document": oldest.created_at.isoformat() if oldest else None,
                "newest_document": newest.created_at.isoformat() if newest else None,
                "backend": "PostgreSQL + pgvector",
                "embedding_dimension": 384
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            raise
        finally:
            db.close()


# Singleton instance
_vector_service = None


def get_vector_service() -> VectorService:
    """Get or create VectorService singleton."""
    global _vector_service
    if _vector_service is None:
        _vector_service = VectorService()
    return _vector_service
