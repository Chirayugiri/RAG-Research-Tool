"""
Authentication service with JWT and password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from bson import ObjectId

from models import UserCreate, UserInDB, UserResponse, TokenData
from database import db


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service for user management."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", token_expire_minutes: int = 1440):
        """
        Initialize auth service.
        
        Args:
            secret_key: JWT secret key
            algorithm: JWT algorithm
            token_expire_minutes: Token expiration time in minutes (default: 24 hours)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Data to encode in token
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    async def verify_token(self, token: str) -> TokenData:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            TokenData with user_id
            
        Raises:
            HTTPException: If token is invalid
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            token_data = TokenData(user_id=user_id)
        except JWTError:
            raise credentials_exception
        return token_data
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user response
            
        Raises:
            HTTPException: If username or email already exists
        """
        users_collection = db.get_users_collection()
        
        # Check if username exists
        existing_user = await users_collection.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email exists
        existing_email = await users_collection.find_one({"email": user_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": self.get_password_hash(user_data.password),
            "full_name": user_data.full_name,
            "avatar_url": None,
            "created_at": datetime.utcnow()
        }
        
        result = await users_collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return UserResponse(
            id=str(result.inserted_id),
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            avatar_url=None,
            created_at=user_dict["created_at"]
        )
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username
            password: Plain password
            
        Returns:
            UserInDB if authentication successful, None otherwise
        """
        users_collection = db.get_users_collection()
        user = await users_collection.find_one({"username": username})
        
        if not user:
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            return None
        
        return UserInDB(**user)
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            UserResponse if found, None otherwise
        """
        users_collection = db.get_users_collection()
        
        try:
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                return UserResponse(
                    id=str(user["_id"]),
                    username=user["username"],
                    email=user["email"],
                    full_name=user.get("full_name"),
                    avatar_url=user.get("avatar_url"),
                    created_at=user["created_at"]
                )
        except Exception:
            return None
        
        return None
