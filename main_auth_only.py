#!/usr/bin/env python3
"""
CloneGallery API with Authentication Only (No AI Models)
"""

import os
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
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
    name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.VISITOR

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    username: str
    email: str
    role: str
    avatar: Optional[str] = None
    email_verified: bool = False
    is_active: bool = True
    joined_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Database functions
def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect('clonegallery.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_user(user_data: UserCreate) -> Dict:
    """Create a new user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", 
                      (user_data.email, user_data.username))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="User with this email or username already exists")
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = pwd_context.hash(user_data.password)
        
        cursor.execute("""
            INSERT INTO users (id, email, username, password_hash, name, role, email_verified, is_active, joined_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            user_data.email,
            user_data.username,
            password_hash,
            user_data.name,
            user_data.role.value,
            False,
            True,
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        
        # Return user data
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        return {
            "id": user["id"],
            "name": user["name"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "avatar": user["avatar"],
            "email_verified": bool(user["email_verified"]),
            "is_active": bool(user["is_active"]),
            "joined_at": user["joined_at"]
        }
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Database error creating user: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user with email and password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
        user = cursor.fetchone()
        
        if user and pwd_context.verify(password, user["password_hash"]):
            return {
                "id": user["id"],
                "name": user["name"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "avatar": user["avatar"],
                "email_verified": bool(user["email_verified"]),
                "is_active": bool(user["is_active"]),
                "joined_at": user["joined_at"]
            }
        return None
        
    except sqlite3.Error as e:
        logger.error(f"Database error authenticating user: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()

def create_access_token(user_data: Dict) -> str:
    """Create JWT access token."""
    to_encode = {
        "sub": user_data["id"],
        "email": user_data["email"],
        "username": user_data["username"],
        "role": user_data["role"]
    }
    
    expire = datetime.utcnow() + timezone(timedelta(hours=JWT_EXPIRATION_HOURS))
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

# FastAPI app
app = FastAPI(title="CloneGallery Auth API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "sqlite"
    }

@app.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user."""
    try:
        logger.info(f"Registering user: {user_data.email}")
        user = create_user(user_data)
        logger.info(f"User registered successfully: {user['id']}")
        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Login user and return access token."""
    try:
        logger.info(f"Login attempt for: {login_data.email}")
        user = authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(user)
        
        logger.info(f"User logged in successfully: {user['id']}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(lambda: None)):
    """Get current user info (placeholder - would need proper JWT validation)."""
    # This is a simplified version - in production you'd validate the JWT token
    raise HTTPException(status_code=501, detail="Not implemented")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
