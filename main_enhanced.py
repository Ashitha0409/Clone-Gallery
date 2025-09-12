#!/usr/bin/env python3
"""
Enhanced CloneGallery AI Generator with Database Support
Supports both SQLite (development) and PostgreSQL (production)
"""

import asyncio
import base64
import io
import os
import json
from typing import Optional, List, Union, Dict, Any
import redis
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel
from diffusers import StableDiffusionPipeline, DiffusionPipeline
import logging
import sqlite3
import psycopg2
import psycopg2.extras
from contextlib import asynccontextmanager
import uuid
from datetime import datetime, timezone
import hashlib
import jwt
from passlib.context import CryptContext
import requests
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # 'sqlite' or 'postgresql'
DB_CONFIG = {
    'sqlite': {
        'path': os.getenv('SQLITE_PATH', 'clonegallery.db')
    },
    'postgresql': {
        'host': os.getenv('POSTGRES_HOST', 'postgres'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'database': os.getenv('POSTGRES_DB', 'clonegallery'),
        'user': os.getenv('POSTGRES_USER', 'clonegallery'),
        'password': os.getenv('POSTGRES_PASSWORD', 'clonegallery')
    }
}

# AI Provider configuration
AI_PROVIDER = os.getenv('AI_PROVIDER', 'local')  # 'local', 'replicate', 'openai'
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Global variables
clip_model = None
clip_processor = None
diffusion_pipeline = None
redis_client = None
db_connection = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Pydantic models
class UserRole(str, Enum):
    ADMIN = "Admin"
    EDITOR = "Editor"
    VISITOR = "Visitor"

class PrivacyLevel(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class ImageFormat(str, Enum):
    JPEG = "JPEG"
    PNG = "PNG"
    GIF = "GIF"
    WEBP = "WebP"
    AVIF = "AVIF"
    TIFF = "TIFF"

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

class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation")
    width: Optional[int] = Field(default=512, ge=256, le=1024, description="Image width")
    height: Optional[int] = Field(default=512, ge=256, le=1024, description="Image height")
    num_inference_steps: Optional[int] = Field(default=20, ge=10, le=100, description="Number of inference steps")
    guidance_scale: Optional[float] = Field(default=7.5, ge=1.0, le=20.0, description="Guidance scale")
    negative_prompt: Optional[str] = Field(default="", description="Negative prompt")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    model: Optional[str] = Field(default="stable-diffusion-v1-5", description="Model to use")

class GenerateImageResponse(BaseModel):
    image_url: str
    prompt: str
    model: str
    generation_time_ms: int
    cost_usd: Optional[float] = None

class ImageUpload(BaseModel):
    title: str = Field(..., description="Image title")
    caption: Optional[str] = Field(default="", description="Image caption")
    alt_text: Optional[str] = Field(default="", description="Alt text for accessibility")
    privacy: PrivacyLevel = Field(default=PrivacyLevel.PUBLIC, description="Privacy level")
    tags: List[str] = Field(default=[], description="Image tags")

class ImageResponse(BaseModel):
    id: str
    title: str
    caption: Optional[str]
    alt_text: Optional[str]
    url: str
    thumbnail: str
    uploader_id: str
    uploaded_at: datetime
    privacy: PrivacyLevel
    views: int
    is_ai_generated: bool
    width: Optional[int]
    height: Optional[int]
    size_bytes: Optional[int]
    format: Optional[ImageFormat]
    tags: List[str] = []

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    filters: Optional[Dict[str, Any]] = Field(default={}, description="Search filters")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")

class SearchResponse(BaseModel):
    images: List[ImageResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# Database connection management
def get_db_connection():
    """Get database connection based on configuration."""
    global db_connection
    
    if db_connection is None:
        if DB_TYPE == 'sqlite':
            db_connection = sqlite3.connect(DB_CONFIG['sqlite']['path'])
            db_connection.row_factory = sqlite3.Row
        elif DB_TYPE == 'postgresql':
            db_connection = psycopg2.connect(**DB_CONFIG['postgresql'])
            db_connection.autocommit = False
        else:
            raise ValueError(f"Unsupported database type: {DB_TYPE}")
    
    return db_connection

def close_db_connection():
    """Close database connection."""
    global db_connection
    if db_connection:
        db_connection.close()
        db_connection = None

# Database operations
class DatabaseManager:
    def __init__(self):
        self.conn = get_db_connection()
    
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
        """Execute a database query."""
        try:
            if DB_TYPE == 'sqlite':
                cursor = self.conn.cursor()
                cursor.execute(query, params or ())
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    self.conn.commit()
                    return cursor.lastrowid
            else:  # PostgreSQL
                with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    if fetch_one:
                        return cursor.fetchone()
                    elif fetch_all:
                        return cursor.fetchall()
                    else:
                        self.conn.commit()
                        return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Database query failed: {e}")
            raise HTTPException(status_code=500, detail="Database operation failed")
    
    def create_user(self, user_data: UserCreate) -> str:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        password_hash = pwd_context.hash(user_data.password)
        
        query = """
            INSERT INTO users (id, email, username, password_hash, name, role, joined_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """ if DB_TYPE == 'sqlite' else """
            INSERT INTO users (id, email, username, password_hash, name, role, joined_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            user_id, user_data.email, user_data.username, password_hash,
            user_data.name, user_data.role.value, datetime.now(timezone.utc)
        )
        
        self.execute_query(query, params)
        return user_id
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data."""
        query = """
            SELECT id, email, username, password_hash, name, role, avatar, email_verified, 
                   is_active, last_login, joined_at, uploads, views
            FROM users WHERE email = ? AND is_active = true
        """ if DB_TYPE == 'sqlite' else """
            SELECT id, email, username, password_hash, name, role, avatar, email_verified, 
                   is_active, last_login, joined_at, uploads, views
            FROM users WHERE email = %s AND is_active = true
        """
        
        user = self.execute_query(query, (email,), fetch_one=True)
        if user and pwd_context.verify(password, user['password_hash']):
            # Update last login
            update_query = """
                UPDATE users SET last_login = ? WHERE id = ?
            """ if DB_TYPE == 'sqlite' else """
                UPDATE users SET last_login = %s WHERE id = %s
            """
            self.execute_query(update_query, (datetime.now(timezone.utc), user['id']))
            return dict(user)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        query = """
            SELECT id, email, username, name, role, avatar, email_verified, 
                   is_active, last_login, joined_at, uploads, views
            FROM users WHERE id = ?
        """ if DB_TYPE == 'sqlite' else """
            SELECT id, email, username, name, role, avatar, email_verified, 
                   is_active, last_login, joined_at, uploads, views
            FROM users WHERE id = %s
        """
        
        user = self.execute_query(query, (user_id,), fetch_one=True)
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

# AI Generation functions
async def generate_image_local(prompt: str, width: int, height: int, 
                             num_inference_steps: int, guidance_scale: float,
                             negative_prompt: str = "", seed: Optional[int] = None) -> str:
    """Generate image using local Stable Diffusion model."""
    if diffusion_pipeline is None:
        raise HTTPException(status_code=503, detail="AI model not loaded")
    
    try:
        generator = torch.Generator(device=device)
        if seed is not None:
            generator.manual_seed(seed)
        
        start_time = datetime.now()
        
        image = diffusion_pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator
        ).images[0]
        
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        logger.info(f"Generated image in {generation_time:.2f}ms")
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        logger.error(f"Local image generation failed: {e}")
        raise HTTPException(status_code=500, detail="Image generation failed")

async def generate_image_replicate(prompt: str, width: int, height: int,
                                 num_inference_steps: int, guidance_scale: float,
                                 negative_prompt: str = "", seed: Optional[int] = None) -> str:
    """Generate image using Replicate API."""
    if not REPLICATE_API_TOKEN:
        raise HTTPException(status_code=503, detail="Replicate API not configured")
    
    try:
        headers = {
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "version": "ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "seed": seed
            }
        }
        
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code != 201:
            raise HTTPException(status_code=500, detail="Replicate API error")
        
        prediction = response.json()
        prediction_id = prediction["id"]
        
        # Poll for completion
        while True:
            status_response = requests.get(
                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                headers=headers,
                timeout=30
            )
            
            if status_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to check generation status")
            
            status_data = status_response.json()
            
            if status_data["status"] == "succeeded":
                return status_data["output"][0]
            elif status_data["status"] == "failed":
                raise HTTPException(status_code=500, detail="Image generation failed")
            
            await asyncio.sleep(2)
            
    except requests.RequestException as e:
        logger.error(f"Replicate API request failed: {e}")
        raise HTTPException(status_code=500, detail="External API error")

# Model loading
def load_models():
    """Load AI models."""
    global clip_model, clip_processor, diffusion_pipeline
    
    try:
        logger.info("Loading CLIP model...")
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        if AI_PROVIDER == 'local' and torch.cuda.is_available():
            logger.info("Loading Stable Diffusion model...")
            diffusion_pipeline = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            diffusion_pipeline = diffusion_pipeline.to(device)
            diffusion_pipeline.enable_attention_slicing()
            
        logger.info("Models loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        if AI_PROVIDER == 'local':
            logger.warning("Falling back to external AI providers")

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting CloneGallery AI Generator...")
    
    # Initialize Redis
    global redis_client
    try:
        redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'cache'), port=6379, decode_responses=True)
        redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        redis_client = None
    
    # Load AI models
    load_models()
    
    yield
    
    # Shutdown
    logger.info("Shutting down CloneGallery AI Generator...")
    close_db_connection()

# Initialize FastAPI app
app = FastAPI(
    title="CloneGallery AI Generator",
    version="2.0.0",
    description="Enhanced AI-powered image generation with database support",
    lifespan=lifespan
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
        "database": DB_TYPE,
        "ai_provider": AI_PROVIDER,
        "device": device
    }

@app.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: DatabaseManager = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.execute_query(
        "SELECT id FROM users WHERE email = ?" if DB_TYPE == 'sqlite' else "SELECT id FROM users WHERE email = %s",
        (user_data.email,),
        fetch_one=True
    )
    
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

@app.post("/generate/image", response_model=GenerateImageResponse)
async def generate_image(
    request: GenerateImageRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Generate an image using AI."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    start_time = datetime.now()
    
    try:
        if AI_PROVIDER == 'local' and diffusion_pipeline is not None:
            image_url = await generate_image_local(
                request.prompt, request.width, request.height,
                request.num_inference_steps, request.guidance_scale,
                request.negative_prompt, request.seed
            )
            model = "stable-diffusion-v1-5"
            cost = None
        elif AI_PROVIDER == 'replicate':
            image_url = await generate_image_replicate(
                request.prompt, request.width, request.height,
                request.num_inference_steps, request.guidance_scale,
                request.negative_prompt, request.seed
            )
            model = "replicate/stable-diffusion"
            cost = 0.01  # Approximate cost
        else:
            raise HTTPException(status_code=503, detail="No AI provider available")
        
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return GenerateImageResponse(
            image_url=image_url,
            prompt=request.prompt,
            model=model,
            generation_time_ms=int(generation_time),
            cost_usd=cost
        )
        
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail="Image generation failed")

@app.get("/models/status")
async def get_models_status():
    """Get status of loaded AI models."""
    return {
        "clip_loaded": clip_model is not None,
        "diffusion_loaded": diffusion_pipeline is not None,
        "device": device,
        "ai_provider": AI_PROVIDER,
        "cuda_available": torch.cuda.is_available()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
