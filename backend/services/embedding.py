"""
Vector storage service using Pinecone and Eden AI embeddings.
"""

import os
import time
import requests
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec


class EmbeddingService:
    """Service for generating embeddings and managing vector storage."""
    
    def __init__(self, api_key: str, edenai_api_key: str, index_name: str):
        """
        Initialize embedding service.
        
        Args:
            api_key: Pinecone API key
            edenai_api_key: Eden AI API key
            index_name: Name of Pinecone index
        """
        self.edenai_api_key = edenai_api_key
        self.index_name = index_name
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)
        
        # Create or get index
        self._ensure_index_exists()
        self.index = self.pc.Index(index_name)
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist."""
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=4096,  # Cohere embedding dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            # Wait for index to be ready
            time.sleep(1)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Eden AI (Cohere).
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (4096 dimensions)
        """
        url = "https://api.edenai.run/v2/text/embeddings"
        
        headers = {
            "Authorization": f"Bearer {self.edenai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "providers": "cohere",
            "texts": [text],
            "settings": {
                "cohere": "embed-english-v3.0"
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Eden AI returns response with key format: 'cohere/4096__embed-english-v2.0'
            # Find the cohere key (it varies based on model version)
            cohere_key = None
            for key in result.keys():
                if key.startswith('cohere'):
                    cohere_key = key
                    break
            
            if cohere_key and 'items' in result[cohere_key]:
                return result[cohere_key]['items'][0]['embedding']
            else:
                raise Exception(f"Invalid response from Eden AI API. Response keys: {list(result.keys())}")
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def store_documents(self, chunks: List[Any]) -> Dict[str, Any]:
        """
        Store document chunks in Pinecone.
        
        Args:
            chunks: List of document chunks from LangChain
            
        Returns:
            Dictionary with storage status
        """
        try:
            vectors = []
            
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self.generate_embedding(chunk.page_content)
                
                # Prepare metadata
                metadata = {
                    "text": chunk.page_content,
                    "source": chunk.metadata.get("source", ""),
                    "chunk_id": i
                }
                
                # Create vector
                vector_id = f"chunk_{i}_{int(time.time())}"
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })
                
                # Batch upsert every 50 vectors
                if len(vectors) >= 50:
                    self.index.upsert(vectors=vectors)
                    vectors = []
            
            # Upsert remaining vectors
            if vectors:
                self.index.upsert(vectors=vectors)
            
            return {
                "success": True,
                "num_stored": len(chunks),
                "message": f"Successfully stored {len(chunks)} chunks"
            }
        except Exception as e:
            return {
                "success": False,
                "num_stored": 0,
                "error": str(e)
            }
    
    def search_similar(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            documents = []
            for match in results.matches:
                documents.append({
                    "text": match.metadata.get("text", ""),
                    "source": match.metadata.get("source", ""),
                    "score": match.score
                })
            
            return documents
        except Exception as e:
            raise Exception(f"Failed to search: {str(e)}")
    
    def clear_index(self) -> Dict[str, Any]:
        """
        Clear all vectors from the index.
        
        Returns:
            Dictionary with clear status
        """
        try:
            self.index.delete(delete_all=True)
            return {
                "success": True,
                "message": "Index cleared successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
