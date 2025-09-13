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
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends, Query, Form
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
    
    def execute(self, query: str, params: tuple = None):
        """Execute a query and return cursor."""
        if DB_TYPE == 'sqlite':
            cursor = self.conn.cursor()
            cursor.execute(query, params or ())
            return cursor
        else:  # PostgreSQL
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor
    
    def fetch_one(self, query: str, params: tuple = None):
        """Fetch one row."""
        return self.execute_query(query, params, fetch_one=True)
    
    def fetch_all(self, query: str, params: tuple = None):
        """Fetch all rows."""
        return self.execute_query(query, params, fetch_all=True)
    
    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()
    
    def get_or_create_tag(self, tag_name: str) -> int:
        """Get or create a tag and return its ID."""
        # Try to get existing tag
        tag = self.fetch_one("SELECT id FROM tags WHERE name = ?", (tag_name,))
        if tag:
            return tag['id']
        
        # Create new tag
        cursor = self.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
        self.commit()
        return cursor.lastrowid

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
        "ai_provider": AI_PROVIDER
    }

# Image upload and management endpoints
@app.post("/upload/image", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    title: str = Form(...),
    caption: str = Form(""),
    alt_text: str = Form(""),
    privacy: PrivacyLevel = Form(PrivacyLevel.PUBLIC),
    tags: str = Form(""),  # Comma-separated tags
    current_user: Dict = Depends(get_current_user)
):
    """Upload an image file."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read file data
        file_data = await file.read()
        
        # Upload to storage service
        from storage_service import StorageService
        storage = StorageService()
        file_url, thumbnail_url = storage.upload_file(
            file_data, file.filename, file.content_type
        )
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Get image dimensions
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(file_data))
        width, height = image.size
        
        # Save to database
        db = DatabaseManager()
        image_id = str(uuid.uuid4())
        
        # Insert image record
        db.execute("""
            INSERT INTO images (id, title, caption, alt_text, url, thumbnail, 
                              uploader_id, privacy, width, height, size_bytes, 
                              format, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            image_id, title, caption, alt_text, file_url, thumbnail_url,
            current_user['id'], privacy.value, width, height, len(file_data),
            file.content_type.split('/')[1].upper(), datetime.now(timezone.utc)
        ))
        
        # Insert tags
        for tag_name in tag_list:
            tag_id = db.get_or_create_tag(tag_name)
            db.execute("""
                INSERT OR IGNORE INTO image_tags (image_id, tag_id)
                VALUES (?, ?)
            """, (image_id, tag_id))
        
        # Update user upload count
        db.execute("""
            UPDATE users SET uploads = uploads + 1 WHERE id = ?
        """, (current_user['id'],))
        
        db.commit()
        
        # Return image response
        return ImageResponse(
            id=image_id,
            title=title,
            caption=caption,
            alt_text=alt_text,
            url=file_url,
            thumbnail=thumbnail_url,
            uploader_id=current_user['id'],
            uploaded_at=datetime.now(timezone.utc),
            privacy=privacy,
            views=0,
            is_ai_generated=False,
            width=width,
            height=height,
            size_bytes=len(file_data),
            format=ImageFormat(file.content_type.split('/')[1].upper()),
            tags=tag_list
        )
        
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        raise HTTPException(status_code=500, detail="Image upload failed")

@app.get("/images", response_model=SearchResponse)
async def get_images(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    privacy: Optional[PrivacyLevel] = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    """Get images with pagination and filtering."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        db = DatabaseManager()
        
        # Build query based on user role and filters
        where_conditions = []
        params = []
        
        # If user_id is specified, filter by that user
        if user_id:
            where_conditions.append("uploader_id = ?")
            params.append(user_id)
        
        # If privacy filter is specified
        if privacy:
            where_conditions.append("privacy = ?")
            params.append(privacy.value)
        
        # For non-admin users, only show public images or their own images
        if current_user['role'] != 'Admin':
            where_conditions.append("(privacy = 'public' OR uploader_id = ?)")
            params.append(current_user['id'])
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Count total images
        count_query = f"SELECT COUNT(*) as total FROM images {where_clause}"
        total = db.fetch_one(count_query, params)['total']
        
        # Get images with pagination
        offset = (page - 1) * limit
        images_query = f"""
            SELECT i.*, GROUP_CONCAT(t.name) as tag_names
            FROM images i
            LEFT JOIN image_tags it ON i.id = it.image_id
            LEFT JOIN tags t ON it.tag_id = t.id
            {where_clause}
            GROUP BY i.id
            ORDER BY i.uploaded_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        images = db.fetch_all(images_query, params)
        
        # Convert to ImageResponse objects
        image_responses = []
        for img in images:
            tags = img['tag_names'].split(',') if img['tag_names'] else []
            image_responses.append(ImageResponse(
                id=img['id'],
                title=img['title'],
                caption=img['caption'],
                alt_text=img['alt_text'],
                url=img['url'],
                thumbnail=img['thumbnail'],
                uploader_id=img['uploader_id'],
                uploaded_at=datetime.fromisoformat(img['uploaded_at'].replace('Z', '+00:00')),
                privacy=PrivacyLevel(img['privacy']),
                views=img['views'],
                is_ai_generated=bool(img['is_ai_generated']),
                width=img['width'],
                height=img['height'],
                size_bytes=img['size_bytes'],
                format=ImageFormat(img['format']) if img['format'] else None,
                tags=tags
            ))
        
        return SearchResponse(
            images=image_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit
        )
        
    except Exception as e:
        logger.error(f"Failed to get images: {e}")
        raise HTTPException(status_code=500, detail="Failed to get images")

@app.get("/images/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get a specific image by ID."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        db = DatabaseManager()
        
        # Get image with tags
        image_query = """
            SELECT i.*, GROUP_CONCAT(t.name) as tag_names
            FROM images i
            LEFT JOIN image_tags it ON i.id = it.image_id
            LEFT JOIN tags t ON it.tag_id = t.id
            WHERE i.id = ?
            GROUP BY i.id
        """
        
        img = db.fetch_one(image_query, (image_id,))
        if not img:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Check permissions
        if (current_user['role'] != 'Admin' and 
            img['privacy'] == 'private' and 
            img['uploader_id'] != current_user['id']):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Increment view count
        db.execute("UPDATE images SET views = views + 1 WHERE id = ?", (image_id,))
        db.commit()
        
        tags = img['tag_names'].split(',') if img['tag_names'] else []
        return ImageResponse(
            id=img['id'],
            title=img['title'],
            caption=img['caption'],
            alt_text=img['alt_text'],
            url=img['url'],
            thumbnail=img['thumbnail'],
            uploader_id=img['uploader_id'],
            uploaded_at=datetime.fromisoformat(img['uploaded_at'].replace('Z', '+00:00')),
            privacy=PrivacyLevel(img['privacy']),
            views=img['views'] + 1,  # Include the increment
            is_ai_generated=bool(img['is_ai_generated']),
            width=img['width'],
            height=img['height'],
            size_bytes=img['size_bytes'],
            format=ImageFormat(img['format']) if img['format'] else None,
            tags=tags
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get image: {e}")
        raise HTTPException(status_code=500, detail="Failed to get image")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
