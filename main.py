import asyncio
import base64
import io
import os
import uuid
from typing import Optional, List, Union, Dict
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
from datetime import datetime, timezone, timedelta
from enum import Enum
import jwt
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('clonegallery.db')
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        avatar TEXT,
        email_verified INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        joined_at TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized")

# Initialize FastAPI app
app = FastAPI(title="CloneGallery AI Generator", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Redis connection for job queue
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'cache'), port=6379, decode_responses=True)

# Global model instances
clip_model = None
clip_processor = None
diffusion_pipeline = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models for authentication
class UserRole(str, Enum):
    ADMIN = "Admin"
    EDITOR = "Editor"
    VISITOR = "Visitor"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    name: str = Field(None, min_length=1, max_length=100)
    email: str = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    role: UserRole = UserRole.VISITOR

class UserLogin(BaseModel):
    username: str
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

class GenerateImageRequest(BaseModel):
    prompt: str
    width: Optional[int] = 512
    height: Optional[int] = 512
    num_inference_steps: Optional[int] = 20

# Database connection
def get_db_connection():
    """Get SQLite database connection."""
    conn = sqlite3.connect('clonegallery.db')
    conn.row_factory = sqlite3.Row
    return conn

# Authentication functions
def create_access_token(data: dict):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_password(plain_password, hashed_password):
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash password."""
    return pwd_context.hash(password)

from fastapi import Header, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Authentication endpoints
@app.post("/auth/register", response_model=TokenResponse)
async def register_user(user: UserCreate):
    """Register a new user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Set default values for optional fields
    name = user.name or user.username
    email = user.email or f"{user.username}@example.com"
    
    # Check if email already exists (if provided)
    if user.email:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    joined_at = datetime.now(timezone.utc).isoformat()
    
    cursor.execute(
        """INSERT INTO users (id, name, username, email, password_hash, role, joined_at, email_verified, is_active, avatar) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, name, user.username, email, hashed_password, user.role, joined_at, False, True, None)
    )
    conn.commit()
    
    # Get the newly created user
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    new_user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id})
    
    # Return token response with user info
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user["id"],
            name=new_user["name"],
            username=new_user["username"],
            email=new_user["email"],
            role=new_user["role"],
            avatar=new_user["avatar"],
            email_verified=new_user["email_verified"],
            is_active=new_user["is_active"],
            joined_at=new_user["joined_at"]
        )
    )

@app.post("/auth/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin):
    """Login user and return JWT token."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Try to find user by username or email
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (user_credentials.username, user_credentials.username))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not user or not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            name=user["name"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            avatar=user["avatar"],
            email_verified=user["email_verified"],
            is_active=user["is_active"],
            joined_at=user["joined_at"]
        )
    )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(token: str = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=token["id"],
        name=token["name"],
        username=token["username"],
        email=token["email"],
        role=token["role"],
        avatar=token["avatar"],
        email_verified=token["email_verified"],
        is_active=token["is_active"],
        joined_at=token["joined_at"]
    )

class ImageResponse(BaseModel):
    id: str
    title: str
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    url: str
    thumbnail_url: Optional[str] = None
    uploader_id: str
    uploaded_at: str
    views: int = 0
    likes: int = 0
    privacy: str = "public"
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: Optional[int] = None
    tags: List[str] = []

class SearchResponse(BaseModel):
    images: List[ImageResponse]
    total: int
    page: int
    limit: int

class AnalyticsResponse(BaseModel):
    total_images: int
    total_users: int
    total_views: int
    total_likes: int
    storage_used: str
    ai_generated: int
    processing_queue: int

# Mock data for images
mock_images = [
    {
        "id": "img-001",
        "title": "Mountain Landscape",
        "caption": "Beautiful mountain view at sunset",
        "alt_text": "Mountains with snow caps at sunset",
        "url": "/uploads/img-001.jpg",
        "thumbnail_url": "/uploads/thumbnails/img-001.jpg",
        "uploader_id": "user-001",
        "uploaded_at": "2024-09-01T10:30:00Z",
        "views": 120,
        "likes": 45,
        "privacy": "public",
        "width": 1920,
        "height": 1080,
        "size_bytes": 2500000,
        "tags": ["nature", "mountains", "landscape"]
    },
    {
        "id": "img-002",
        "title": "Urban Architecture",
        "caption": "Modern city skyline",
        "alt_text": "Skyscrapers in a modern city",
        "url": "/uploads/img-002.jpg",
        "thumbnail_url": "/uploads/thumbnails/img-002.jpg",
        "uploader_id": "user-002",
        "uploaded_at": "2024-09-02T14:45:00Z",
        "views": 85,
        "likes": 32,
        "privacy": "public",
        "width": 1800,
        "height": 1200,
        "size_bytes": 3100000,
        "tags": ["urban", "architecture", "city"]
    },
    {
        "id": "img-003",
        "title": "Ocean Waves",
        "caption": "Powerful ocean waves at the shore",
        "alt_text": "Blue ocean waves crashing on rocks",
        "url": "/uploads/img-003.jpg",
        "thumbnail_url": "/uploads/thumbnails/img-003.jpg",
        "uploader_id": "user-001",
        "uploaded_at": "2024-09-03T09:15:00Z",
        "views": 95,
        "likes": 38,
        "privacy": "public",
        "width": 2000,
        "height": 1333,
        "size_bytes": 2800000,
        "tags": ["nature", "ocean", "waves"]
    }
]

# Image endpoints
@app.get("/images", response_model=SearchResponse)
async def get_images(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    """Get images with pagination and filtering."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Filter images by user_id if provided
    filtered_images = mock_images
    if user_id:
        filtered_images = [img for img in mock_images if img["uploader_id"] == user_id]
    
    # Calculate pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_images = filtered_images[start_idx:end_idx]
    
    # Convert to response model
    image_responses = [ImageResponse(**img) for img in paginated_images]
    
    return SearchResponse(
        images=image_responses,
        total=len(filtered_images),
        page=page,
        limit=limit
    )

@app.get("/images/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get a specific image by ID."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Find the image by ID
    image = next((img for img in mock_images if img["id"] == image_id), None)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return ImageResponse(**image)

@app.get("/dashboard/stats", response_model=AnalyticsResponse)
async def get_dashboard_stats(
    current_user: Dict = Depends(get_current_user)
):
    """Get dashboard statistics."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Mock analytics data
    return AnalyticsResponse(
        total_images=1247,
        total_users=156,
        total_views=45680,
        total_likes=8934,
        storage_used="12.4 GB",
        ai_generated=234,
        processing_queue=3
    )

class GenerateImageRequest(BaseModel):
    prompt: str
    width: Optional[int] = 512
    height: Optional[int] = 512
    num_inference_steps: Optional[int] = 20
    guidance_scale: Optional[float] = 7.5
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    dimensions: int

async def load_models():
    """Load AI models on startup."""
    global clip_model, clip_processor, diffusion_pipeline

    try:
        logger.info("Loading CLIP model...")
        clip_model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32",
            cache_dir=os.getenv('MODEL_CACHE_DIR', '/app/models')
        ).to(device)
        clip_processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32",
            cache_dir=os.getenv('MODEL_CACHE_DIR', '/app/models')
        )

        logger.info("Loading Stable Diffusion pipeline...")
        diffusion_pipeline = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            cache_dir=os.getenv('MODEL_CACHE_DIR', '/app/models'),
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        ).to(device)

        # Enable memory efficient attention if available
        if hasattr(diffusion_pipeline, "enable_attention_slicing"):
            diffusion_pipeline.enable_attention_slicing()

        if hasattr(diffusion_pipeline, "enable_vae_slicing"):
            diffusion_pipeline.enable_vae_slicing()

        logger.info("Models loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    await load_models()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "device": device,
        "models_loaded": {
            "clip": clip_model is not None,
            "diffusion": diffusion_pipeline is not None
        }
    }

@app.post("/embed/text", response_model=EmbeddingResponse)
async def generate_text_embedding(text: str):
    """Generate CLIP text embedding."""
    if clip_model is None or clip_processor is None:
        raise HTTPException(status_code=503, detail="CLIP model not loaded")

    try:
        inputs = clip_processor(text=[text], return_tensors="pt", padding=True).to(device)

        with torch.no_grad():
            text_features = clip_model.get_text_features(**inputs)
            # Normalize embeddings
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        embedding = text_features.cpu().numpy().flatten().tolist()

        return EmbeddingResponse(
            embedding=embedding,
            dimensions=len(embedding)
        )

    except Exception as e:
        logger.error(f"Text embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate embedding")

@app.post("/embed/image", response_model=EmbeddingResponse)
async def generate_image_embedding(image: UploadFile = File(...)):
    """Generate CLIP image embedding."""
    if clip_model is None or clip_processor is None:
        raise HTTPException(status_code=503, detail="CLIP model not loaded")

    try:
        # Read and process image
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data)).convert('RGB')

        inputs = clip_processor(images=pil_image, return_tensors="pt").to(device)

        with torch.no_grad():
            image_features = clip_model.get_image_features(**inputs)
            # Normalize embeddings
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        embedding = image_features.cpu().numpy().flatten().tolist()

        return EmbeddingResponse(
            embedding=embedding,
            dimensions=len(embedding)
        )

    except Exception as e:
        logger.error(f"Image embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate embedding")

@app.post("/generate/image")
async def generate_image(
    request: GenerateImageRequest,
    background_tasks: BackgroundTasks
):
    """Generate image using Stable Diffusion."""
    if diffusion_pipeline is None:
        raise HTTPException(status_code=503, detail="Diffusion model not loaded")

    try:
        # Set seed for reproducible results
        if request.seed:
            torch.manual_seed(request.seed)
            np.random.seed(request.seed)

        # Generate image
        with torch.no_grad():
            result = diffusion_pipeline(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                width=request.width,
                height=request.height,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale,
                generator=torch.Generator(device=device).manual_seed(request.seed or 42)
            )

        # Convert to base64
        image = result.images[0]
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            "image": f"data:image/png;base64,{image_b64}",
            "seed": request.seed or 42,
            "prompt": request.prompt,
            "parameters": {
                "width": request.width,
                "height": request.height,
                "steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale
            }
        }

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image")

@app.get("/models/status")
async def model_status():
    """Get status of loaded models."""
    return {
        "clip_model": "loaded" if clip_model is not None else "not_loaded",
        "diffusion_model": "loaded" if diffusion_pipeline is not None else "not_loaded",
        "device": device,
        "memory_usage": {
            "cuda_memory": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0,
            "cuda_memory_cached": torch.cuda.memory_reserved() if torch.cuda.is_available() else 0
        } if torch.cuda.is_available() else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
