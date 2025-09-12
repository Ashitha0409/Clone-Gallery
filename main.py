import asyncio
import base64
import io
import os
from typing import Optional, List, Union
import redis
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel
from diffusers import StableDiffusionPipeline, DiffusionPipeline
import logging
import sqlite3
import psycopg2
import psycopg2.extras
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Redis connection for job queue
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'cache'), port=6379, decode_responses=True)

# Global model instances
clip_model = None
clip_processor = None
diffusion_pipeline = None
device = "cuda" if torch.cuda.is_available() else "cpu"

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
