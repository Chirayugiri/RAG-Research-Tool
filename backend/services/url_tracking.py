"""
URL Tracking Service for managing processed URLs per user.
"""

from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from database import db


class URLTrackingService:
    """Service for tracking which URLs each user has processed."""
    
    def __init__(self):
        """Initialize URL tracking service."""
        self.collection_name = "processed_urls"
    
    async def _get_collection(self):
        """Get the processed URLs collection."""
        return db.db[self.collection_name]
    
    async def is_url_processed(self, user_id: str, url: str) -> bool:
        """
        Check if a URL has already been processed by a specific user.
        
        Args:
            user_id: User ID
            url: URL to check
            
        Returns:
            True if URL has been processed by this user, False otherwise
        """
        collection = await self._get_collection()
        result = await collection.find_one({
            "user_id": ObjectId(user_id),
            "url": url,
            "status": "success"
        })
        return result is not None
    
    async def mark_url_processed(
        self,
        user_id: str,
        url: str,
        num_chunks: int,
        status: str = "success"
    ) -> bool:
        """
        Mark a URL as processed for a specific user.
        
        Args:
            user_id: User ID
            url: Processed URL
            num_chunks: Number of chunks created
            status: Processing status ("success" or "failed")
            
        Returns:
            True if successfully marked
        """
        collection = await self._get_collection()
        
        # Upsert to handle re-processing
        result = await collection.update_one(
            {
                "user_id": ObjectId(user_id),
                "url": url
            },
            {
                "$set": {
                    "user_id": ObjectId(user_id),
                    "url": url,
                    "processed_at": datetime.utcnow(),
                    "num_chunks": num_chunks,
                    "status": status
                }
            },
            upsert=True
        )
        
        return result.acknowledged
    
    async def get_user_urls(self, user_id: str, limit: int = 100) -> List[Dict]:
        """
        Get all URLs processed by a specific user.
        
        Args:
            user_id: User ID
            limit: Maximum number of URLs to return
            
        Returns:
            List of processed URL documents
        """
        collection = await self._get_collection()
        cursor = collection.find(
            {"user_id": ObjectId(user_id)},
            {"_id": 0, "url": 1, "processed_at": 1, "num_chunks": 1, "status": 1}
        ).sort("processed_at", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def filter_new_urls(self, user_id: str, urls: List[str]) -> Dict[str, List[str]]:
        """
        Filter URLs into new and already-processed for a specific user.
        
        Args:
            user_id: User ID
            urls: List of URLs to filter
            
        Returns:
            Dictionary with "new" and "skipped" URL lists
        """
        new_urls = []
        skipped_urls = []
        
        for url in urls:
            is_processed = await self.is_url_processed(user_id, url)
            if is_processed:
                skipped_urls.append(url)
            else:
                new_urls.append(url)
        
        return {
            "new": new_urls,
            "skipped": skipped_urls
        }
    
    async def create_indexes(self):
        """Create database indexes for efficient querying."""
        collection = await self._get_collection()
        
        # Compound index on (user_id, url) for fast lookups
        await collection.create_index([("user_id", 1), ("url", 1)], unique=True)
        
        # Index on user_id for getting all user URLs
        await collection.create_index([("user_id", 1)])
