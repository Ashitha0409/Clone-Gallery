#!/usr/bin/env python3
"""
Simple CloneGallery API without AI models for testing
"""

import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict
import hashlib
import jwt
from passlib.context import CryptContext
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from enum import Enum

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class UserRole(str, Enum):
    ADMIN = "Admin"
    EDITOR = "Editor"
    VISITOR = "Visitor"

class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., description="Full name")
    role: UserRole = Field(default=UserRole.VISITOR, description="User role")

class UserLogin(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    name: str
    role: UserRole
    avatar: Optional[str] = None
    email_verified: bool
    is_active: bool
    last_login: Optional[datetime]
    joined_at: datetime
    uploads: int
    views: int

# Database operations
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('clonegallery.db')
        self.conn.row_factory = sqlite3.Row
    
    def create_user(self, user_data: UserCreate) -> str:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        password_hash = pwd_context.hash(user_data.password)
        
        query = """
            INSERT INTO users (id, email, username, password_hash, name, role, joined_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            user_id, user_data.email, user_data.username, password_hash,
            user_data.name, user_data.role.value, datetime.now(timezone.utc)
        )
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return user_id
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data."""
        query = """
            SELECT id, email, username, password_hash, name, role, avatar, email_verified, 
                   is_active, last_login, joined_at, uploads, views
            FROM users WHERE email = ? AND is_active = 1
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        if user and pwd_context.verify(password, user['password_hash']):
            # Update last login
            update_query = "UPDATE users SET last_login = ? WHERE id = ?"
            cursor.execute(update_query, (datetime.now(timezone.utc), user['id']))
            self.conn.commit()
            return dict(user)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        query = """
            SELECT id, email, username, name, role, avatar, email_verified, 
                   is_active, last_login, joined_at, uploads, views
            FROM users WHERE id = ?
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None

# JWT token management
def create_access_token(user_id: str, role: str) -> str:
    """Create JWT access token."""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc).timestamp() + (JWT_EXPIRATION_HOURS * 3600)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Initialize FastAPI app
app = FastAPI(
    title="CloneGallery API",
    version="1.0.0",
    description="Simple API for testing without AI models"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for database
def get_db():
    return DatabaseManager()

# Dependency for authentication
def get_current_user(token: str = Depends(lambda: None)) -> Optional[Dict]:
    """Get current user from JWT token."""
    if not token:
        return None
    
    payload = verify_token(token)
    if not payload:
        return None
    
    db = get_db()
    return db.get_user_by_id(payload["user_id"])

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "sqlite"
    }

@app.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: DatabaseManager = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    cursor = db.conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user_id = db.create_user(user_data)
    user = db.get_user_by_id(user_id)
    
    return UserResponse(**user)

@app.post("/auth/login")
async def login_user(login_data: UserLogin, db: DatabaseManager = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user["id"], user["role"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current user information."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return UserResponse(**current_user)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


