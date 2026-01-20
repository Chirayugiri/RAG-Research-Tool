"""
Document preprocessing service for loading and chunking news articles.
"""

from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.url_fetcher import URLFetcherService
from services.url_tracking import URLTrackingService


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
        self.url_fetcher = URLFetcherService(timeout=10)
        self.url_tracker = URLTrackingService()
    
    async def load_urls(self, urls: List[str], user_id: str) -> Dict[str, Any]:
        """
        Load documents from URLs using async Playwright with deduplication.
        
        Args:
            urls: List of news article URLs
            user_id: User ID for tracking processed URLs
            
        Returns:
            Dictionary with documents and status info
            
        Raises:
            ValueError: If URLs list is empty or invalid
            Exception: If loading fails
        """
        if not urls:
            raise ValueError("URLs list cannot be empty")
        
        if len(urls) > 10:
            raise ValueError("Maximum 10 URLs allowed")
        
        try:
            # Filter out already-processed URLs for this user
            url_filter = await self.url_tracker.filter_new_urls(user_id, urls)
            new_urls = url_filter["new"]
            skipped_urls = url_filter["skipped"]
            
            documents = []
            failed_urls = []
            
            # Only fetch new URLs
            if new_urls:
                # Fetch URLs using async parallel approach
                fetch_results = await self.url_fetcher.fetch_multiple_async(new_urls)
                
                # Convert to LangChain Documents
                for result in fetch_results:
                    if result['success']:
                        doc = Document(
                            page_content=result['text'],
                            metadata={
                                'source': result['url'],
                                'fetch_method': result['method'],
                                'user_id': user_id
                            }
                        )
                        documents.append(doc)
                    else:
                        failed_urls.append({
                            'url': result['url'],
                            'error': result['error']
                        })
            
            return {
                "documents": documents,
                "new_urls": new_urls,
                "skipped_urls": skipped_urls,
                "failed_urls": failed_urls
            }
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
    
    async def process_urls(self, urls: List[str], user_id: str) -> Dict[str, Any]:
        """
        Load and chunk documents from URLs with user-specific deduplication.
        
        Args:
            urls: List of news article URLs
            user_id: User ID for tracking and isolation
            
        Returns:
            Dictionary with processed documents and detailed metadata
        """
        try:
            # Load documents (with deduplication)
            load_result = await self.load_urls(urls, user_id)
            documents = load_result["documents"]
            
            # Chunk documents
            chunks = self.chunk_documents(documents)
            
            # Track successfully processed URLs
            for doc in documents:
                url = doc.metadata.get('source')
                if url:
                    # Count chunks for this URL
                    url_chunks = [c for c in chunks if c.metadata.get('source') == url]
                    await self.url_tracker.mark_url_processed(
                        user_id=user_id,
                        url=url,
                        num_chunks=len(url_chunks),
                        status="success"
                    )
            
            # Track failed URLs
            for failed in load_result["failed_urls"]:
                await self.url_tracker.mark_url_processed(
                    user_id=user_id,
                    url=failed['url'],
                    num_chunks=0,
                    status="failed"
                )
            
            return {
                "success": True,
                "chunks": chunks,
                "num_documents": len(documents),
                "num_chunks": len(chunks),
                "new_urls": len(load_result["new_urls"]),
                "skipped_urls": len(load_result["skipped_urls"]),
                "failed_urls": len(load_result["failed_urls"]),
                "skipped_url_list": load_result["skipped_urls"],
                "failed_url_list": [f['url'] for f in load_result["failed_urls"]],
                "message": f"Processed {len(documents)} new articles (skipped {len(load_result['skipped_urls'])} duplicates)"
            }
        except Exception as e:
            return {
                "success": False,
                "chunks": [],
                "num_documents": 0,
                "num_chunks": 0,
                "new_urls": 0,
                "skipped_urls": 0,
                "failed_urls": 0,
                "error": str(e)
            }

