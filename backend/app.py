"""
FastAPI backend for RAG News Research Tool with MongoDB and Authentication.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from config import settings
from database import db
from models import (
    UserCreate, UserResponse, Token, LoginRequest,
    ChatCreate, ChatResponse, ChatWithMessages,
    MessageCreate, Source
)
from services.auth import AuthService
from services.chat_history import ChatHistoryService
from services.preprocessing import PreprocessingService
from services.embedding import EmbeddingService
from services.llm import LLMService


# Initialize FastAPI app
app = FastAPI(
    title="RAG News Research Tool API",
    description="AI-powered news research with RAG, authentication, and chat history",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Initialize services
auth_service = AuthService(
    secret_key=settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm,
    token_expire_minutes=settings.access_token_expire_minutes
)
chat_service = ChatHistoryService()
preprocessing_service = PreprocessingService()
embedding_service = EmbeddingService(
    api_key=settings.pinecone_api_key,
    edenai_api_key=settings.edenai_api_key,
    index_name=settings.pinecone_index_name
)
llm_service = LLMService(api_key=settings.chat_groq_api_key)


# Dependency to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Get current authenticated user from token."""
    token_data = await auth_service.verify_token(token)
    user = await auth_service.get_user_by_id(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Database lifecycle events
@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup."""
    await db.connect_db(settings.mongodb_uri, settings.mongodb_db_name)


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown."""
    await db.close_db()


# Request/Response models
class URLsRequest(BaseModel):
    urls: List[str]
    chat_id: str = None  # Optional chat ID to associate processed URLs


class QuestionRequest(BaseModel):
    question: str
    chat_id: str = None  # Optional - chat features require authentication


class ProcessResponse(BaseModel):
    success: bool
    message: str
    num_documents: int
    num_chunks: int
    new_urls: int = 0
    skipped_urls: int = 0
    failed_urls: int = 0
    skipped_url_list: List[str] = []
    failed_url_list: List[str] = []


class AnswerResponse(BaseModel):
    success: bool
    answer: str
    sources: List[Source]
    message_id: Optional[str] = None  # ID of saved message (None when not authenticated)


# ===========================
# Authentication Routes
# ===========================

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    user = await auth_service.register_user(user_data)
    return user


@app.post("/api/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Login and get access token."""
    user = await auth_service.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information."""
    return current_user


# ===========================
# Chat History Routes
# ===========================

@app.post("/api/chats", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new chat session."""
    chat = await chat_service.create_chat(current_user.id, chat_data)
    return chat


@app.get("/api/chats", response_model=List[ChatResponse])
async def get_user_chats(
    current_user: UserResponse = Depends(get_current_user),
    limit: int = 50
):
    """Get all chats for the current user."""
    chats = await chat_service.get_user_chats(current_user.id, limit=limit)
    return chats


@app.get("/api/chats/{chat_id}", response_model=ChatWithMessages)
async def get_chat(
    chat_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific chat with all messages."""
    chat_with_messages = await chat_service.get_chat_with_messages(chat_id, current_user.id)
    return chat_with_messages


@app.delete("/api/chats/{chat_id}")
async def delete_chat(
    chat_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a chat session."""
    success = await chat_service.delete_chat(chat_id, current_user.id)
    return {"success": success, "message": "Chat deleted successfully"}


# ===========================
# RAG Routes (with chat integration)
# ===========================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "message": "RAG News Research Tool API with Authentication",
        "version": "2.0.0"
    }


@app.post("/api/process-urls", response_model=ProcessResponse)
async def process_urls(
    request: URLsRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Process news article URLs and store them in user-specific vector database namespace.
    Requires authentication for user data isolation.
    """
    try:
        # Validate URLs
        if not request.urls:
            raise HTTPException(status_code=400, detail="URLs list cannot be empty")
        
        if len(request.urls) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 URLs allowed")
        
        # Process URLs with user-specific deduplication
        result = await preprocessing_service.process_urls(request.urls, str(current_user.id))
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))
        
        # Store in user-specific Pinecone namespace
        if result["chunks"]:
            storage_result = embedding_service.store_documents(result["chunks"], str(current_user.id))
            
            if not storage_result["success"]:
                raise HTTPException(status_code=500, detail=storage_result.get("error", "Storage failed"))
        
        # Update chat with processed URLs if chat_id provided
        if request.chat_id:
            # Get successfully processed URLs (new ones only)
            successfully_processed = [url for url in request.urls if url not in result.get("failed_url_list", [])]
            if successfully_processed:
                await chat_service.update_chat_urls(request.chat_id, str(current_user.id), successfully_processed)
        
        return ProcessResponse(
            success=True,
            message=result["message"],
            num_documents=result["num_documents"],
            num_chunks=result["num_chunks"],
            new_urls=result["new_urls"],
            skipped_urls=result["skipped_urls"],
            failed_urls=result["failed_urls"],
            skipped_url_list=result.get("skipped_url_list", []),
            failed_url_list=result.get("failed_url_list", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Answer a question using RAG from user-specific knowledge base.
    Requires authentication for user data isolation.
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Search for relevant documents in user's namespace
        relevant_docs = embedding_service.search_similar(request.question, str(current_user.id), top_k=4)
        
        # Generate answer using LLM
        answer_result = llm_service.generate_answer(request.question, relevant_docs)
        
        # Save Q&A to chat history if chat_id is provided
        user_message_id = None
        ai_message_id = None
        if request.chat_id:
            # Save user question
            user_message = await chat_service.save_message(
                user_id=str(current_user.id),
                message_data=MessageCreate(
                    chat_id=request.chat_id,
                    type="user",
                    content=request.question,
                    sources=[]
                )
            )
            user_message_id = user_message.id
            
            # Save AI answer
            ai_message = await chat_service.save_message(
                user_id=str(current_user.id),
                message_data=MessageCreate(
                    chat_id=request.chat_id,
                    type="ai",
                    content=answer_result["answer"],
                    sources=[Source(**src) for src in answer_result.get("sources", [])]
                )
            )
            ai_message_id = ai_message.id
        
        return AnswerResponse(
            success=answer_result["success"],
            answer=answer_result["answer"],
            sources=[Source(**src) for src in answer_result.get("sources", [])],
            message_id=ai_message_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear-index")
async def clear_index(current_user: UserResponse = Depends(get_current_user)):
    """Clear user's documents from vector database (user-specific namespace)."""
    try:
        result = embedding_service.clear_user_namespace(str(current_user.id))
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Clear failed"))
        
        return {
            "success": True,
            "message": "Your documents cleared successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/me/urls")
async def get_my_urls(
    current_user: UserResponse = Depends(get_current_user),
    limit: int = 100
):
    """Get current user's processed URLs."""
    from services.url_tracking import URLTrackingService
    
    try:
        url_tracker = URLTrackingService()
        urls = await url_tracker.get_user_urls(str(current_user.id), limit=limit)
        
        return {
            "success": True,
            "urls": urls,
            "count": len(urls)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
