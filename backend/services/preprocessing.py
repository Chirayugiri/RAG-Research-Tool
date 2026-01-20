"""
Document preprocessing service for loading and chunking news articles.
"""

from typing import List, Dict, Any
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PreprocessingService:
    """Service for loading and processing news articles from URLs."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize preprocessing service.
        
        Args:
            chunk_size: Size of text chunks (default: 1000 characters)
            chunk_overlap: Overlap between chunks (default: 200 characters)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def load_urls(self, urls: List[str]) -> List[Any]:
        """
        Load documents from URLs.
        
        Args:
            urls: List of news article URLs
            
        Returns:
            List of loaded documents
            
        Raises:
            ValueError: If URLs list is empty or invalid
            Exception: If loading fails
        """
        if not urls:
            raise ValueError("URLs list cannot be empty")
        
        if len(urls) > 10:
            raise ValueError("Maximum 10 URLs allowed")
        
        try:
            loader = UnstructuredURLLoader(urls=urls)
            documents = loader.load()
            return documents
        except Exception as e:
            raise Exception(f"Failed to load URLs: {str(e)}")
    
    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List of document chunks
        """
        if not documents:
            return []
        
        chunks = self.text_splitter.split_documents(documents)
        return chunks
    
    def process_urls(self, urls: List[str]) -> Dict[str, Any]:
        """
        Load and chunk documents from URLs.
        
        Args:
            urls: List of news article URLs
            
        Returns:
            Dictionary with processed documents and metadata
        """
        try:
            # Load documents
            documents = self.load_urls(urls)
            
            # Chunk documents
            chunks = self.chunk_documents(documents)
            
            return {
                "success": True,
                "chunks": chunks,
                "num_documents": len(documents),
                "num_chunks": len(chunks),
                "message": f"Successfully processed {len(documents)} documents into {len(chunks)} chunks"
            }
        except Exception as e:
            return {
                "success": False,
                "chunks": [],
                "num_documents": 0,
                "num_chunks": 0,
                "error": str(e)
            }
