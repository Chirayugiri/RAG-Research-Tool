"""
MongoDB database connection and initialization.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database manager."""
    
    client: AsyncIOMotorClient = None
    db = None
    
    @classmethod
    async def connect_db(cls, mongodb_uri: str, db_name: str = "rag_news_tool"):
        """Connect to MongoDB."""
        try:
            # SSL/TLS parameters are now included in the mongodb_uri
            cls.client = AsyncIOMotorClient(mongodb_uri)
            # Test connection
            await cls.client.admin.command('ping')
            cls.db = cls.client[db_name]
            
            # Create indexes
            await cls._create_indexes()
            
            logger.info(f"Successfully connected to MongoDB database: {db_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def _create_indexes(cls):
        """Create database indexes for better performance."""
        # Users collection indexes
        await cls.db.users.create_index("username", unique=True)
        await cls.db.users.create_index("email", unique=True)
        
        # Chat sessions indexes
        await cls.db.chat_sessions.create_index("user_id")
        await cls.db.chat_sessions.create_index([("user_id", 1), ("updated_at", -1)])
        
        # Messages indexes
        await cls.db.messages.create_index("chat_id")
        await cls.db.messages.create_index([("chat_id", 1), ("timestamp", 1)])
        
        logger.info("Database indexes created successfully")
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")
    
    @classmethod
    def get_users_collection(cls):
        """Get users collection."""
        return cls.db.users
    
    @classmethod
    def get_chats_collection(cls):
        """Get chat sessions collection."""
        return cls.db.chat_sessions
    
    @classmethod
    def get_messages_collection(cls):
        """Get messages collection."""
        return cls.db.messages


# Global database instance
db = Database()
