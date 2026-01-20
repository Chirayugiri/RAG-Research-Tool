"""
Pydantic models for request/response validation and MongoDB documents.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Annotated
from datetime import datetime
from bson import ObjectId


# Custom ObjectId type for Pydantic v2
class PyObjectId(str):
    """Custom ObjectId type for Pydantic v2."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ], serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)))
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")



# User Models
class UserCreate(BaseModel):
    """User registration model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserInDB(BaseModel):
    """User model in database."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: str
    password_hash: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserResponse(BaseModel):
    """User response model (without password)."""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime


# Authentication Models
class Token(BaseModel):
    """JWT token model."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload."""
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


# Source Model
class Source(BaseModel):
    """Source citation model."""
    url: str
    text: str


# Message Models
class MessageCreate(BaseModel):
    """Create message model."""
    chat_id: str
    type: str  # 'user' or 'ai'
    content: str
    sources: Optional[List[Source]] = []


class MessageInDB(BaseModel):
    """Message model in database."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    chat_id: str
    user_id: str
    type: str
    content: str
    sources: List[Source] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MessageResponse(BaseModel):
    """Message response model."""
    id: str
    type: str
    content: str
    sources: List[Source] = []
    timestamp: datetime


# Chat Session Models
class ChatCreate(BaseModel):
    """Create chat session model."""
    title: Optional[str] = "New Chat"
    processed_urls: Optional[List[str]] = []


class ChatSessionInDB(BaseModel):
    """Chat session model in database."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
    processed_urls: List[str] = []
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ChatResponse(BaseModel):
    """Chat session response model."""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    processed_urls: List[str] = []


class ChatWithMessages(BaseModel):
    """Chat with messages response."""
    chat: ChatResponse
    messages: List[MessageResponse]
