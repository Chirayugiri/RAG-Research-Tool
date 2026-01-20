"""
Chat history management service for MongoDB.
"""

from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from models import (
    ChatCreate, ChatSessionInDB, ChatResponse,
    MessageCreate, MessageInDB, MessageResponse,
    ChatWithMessages
)
from database import db


class ChatHistoryService:
    """Service for managing chat sessions and messages."""
    
    async def create_chat(self, user_id: str, chat_data: ChatCreate) -> ChatResponse:
        """
        Create a new chat session.
        
        Args:
            user_id: User ID
            chat_data: Chat creation data
            
        Returns:
            Created chat response
        """
        chats_collection = db.get_chats_collection()
        
        chat_dict = {
            "user_id": user_id,
            "title": chat_data.title or "New Chat",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0,
            "processed_urls": chat_data.processed_urls or []
        }
        
        result = await chats_collection.insert_one(chat_dict)
        chat_dict["_id"] = result.inserted_id
        
        return ChatResponse(
            id=str(result.inserted_id),
            title=chat_dict["title"],
            created_at=chat_dict["created_at"],
            updated_at=chat_dict["updated_at"],
            message_count=0,
            processed_urls=chat_dict["processed_urls"]
        )
    
    async def get_user_chats(self, user_id: str, limit: int = 50) -> List[ChatResponse]:
        """
        Get all chat sessions for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of chats to return
            
        Returns:
            List of chat responses, sorted by most recent
        """
        chats_collection = db.get_chats_collection()
        
        cursor = chats_collection.find({"user_id": user_id}).sort("updated_at", -1).limit(limit)
        chats = await cursor.to_list(length=limit)
        
        return [
            ChatResponse(
                id=str(chat["_id"]),
                title=chat["title"],
                created_at=chat["created_at"],
                updated_at=chat["updated_at"],
                message_count=chat["message_count"],
                processed_urls=chat.get("processed_urls", [])
            )
            for chat in chats
        ]
    
    async def get_chat_with_messages(self, chat_id: str, user_id: str) -> ChatWithMessages:
        """
        Get chat session with all messages.
        
        Args:
            chat_id: Chat ID
            user_id: User ID (for authorization)
            
        Returns:
            Chat with messages
            
        Raises:
            HTTPException: If chat not found or unauthorized
        """
        chats_collection = db.get_chats_collection()
        messages_collection = db.get_messages_collection()
        
        # Get chat
        try:
            chat = await chats_collection.find_one({"_id": ObjectId(chat_id)})
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        # Check authorization
        if chat["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this chat"
            )
        
        # Get messages
        cursor = messages_collection.find({"chat_id": chat_id}).sort("timestamp", 1)
        messages = await cursor.to_list(length=1000)
        
        chat_response = ChatResponse(
            id=str(chat["_id"]),
            title=chat["title"],
            created_at=chat["created_at"],
            updated_at=chat["updated_at"],
            message_count=chat["message_count"],
            processed_urls=chat.get("processed_urls", [])
        )
        
        message_responses = [
            MessageResponse(
                id=str(msg["_id"]),
                type=msg["type"],
                content=msg["content"],
                sources=msg.get("sources", []),
                timestamp=msg["timestamp"]
            )
            for msg in messages
        ]
        
        return ChatWithMessages(chat=chat_response, messages=message_responses)
    
    async def save_message(self, user_id: str, message_data: MessageCreate) -> MessageResponse:
        """
        Save a message to chat history.
        
        Args:
            user_id: User ID
            message_data: Message data
            
        Returns:
            Saved message response
            
        Raises:
            HTTPException: If chat not found or unauthorized
        """
        chats_collection = db.get_chats_collection()
        messages_collection = db.get_messages_collection()
        
        # Verify chat exists and user owns it
        try:
            chat = await chats_collection.find_one({"_id": ObjectId(message_data.chat_id)})
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        if chat["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add messages to this chat"
            )
        
        # Create message
        message_dict = {
            "chat_id": message_data.chat_id,
            "user_id": user_id,
            "type": message_data.type,
            "content": message_data.content,
            "sources": [source.dict() for source in message_data.sources],
            "timestamp": datetime.utcnow()
        }
        
        result = await messages_collection.insert_one(message_dict)
        message_dict["_id"] = result.inserted_id
        
        # Update chat metadata
        update_data = {
            "updated_at": datetime.utcnow(),
            "message_count": chat["message_count"] + 1
        }
        
        # Auto-generate title from first user message
        if chat["message_count"] == 0 and message_data.type == "user":
            title = message_data.content[:50] + ("..." if len(message_data.content) > 50 else "")
            update_data["title"] = title
        
        await chats_collection.update_one(
            {"_id": ObjectId(message_data.chat_id)},
            {"$set": update_data}
        )
        
        return MessageResponse(
            id=str(result.inserted_id),
            type=message_data.type,
            content=message_data.content,
            sources=message_data.sources,
            timestamp=message_dict["timestamp"]
        )
    
    async def delete_chat(self, chat_id: str, user_id: str) -> bool:
        """
        Delete a chat session and all its messages.
        
        Args:
            chat_id: Chat ID
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted successfully
            
        Raises:
            HTTPException: If chat not found or unauthorized
        """
        chats_collection = db.get_chats_collection()
        messages_collection = db.get_messages_collection()
        
        # Verify chat exists and user owns it
        try:
            chat = await chats_collection.find_one({"_id": ObjectId(chat_id)})
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        if chat["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this chat"
            )
        
        # Delete all messages in chat
        await messages_collection.delete_many({"chat_id": chat_id})
        
        # Delete chat
        await chats_collection.delete_one({"_id": ObjectId(chat_id)})
        
        return True
    
    async def update_chat_urls(self, chat_id: str, user_id: str, urls: List[str]) -> bool:
        """
        Update processed URLs for a chat.
        
        Args:
            chat_id: Chat ID
            user_id: User ID (for authorization)
            urls: List of processed URLs
            
        Returns:
            True if updated successfully
        """
        chats_collection = db.get_chats_collection()
        
        # Verify chat exists and user owns it
        try:
            chat = await chats_collection.find_one({"_id": ObjectId(chat_id)})
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        if chat["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this chat"
            )
        
        # Update URLs
        await chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"processed_urls": urls, "updated_at": datetime.utcnow()}}
        )
        
        return True
