# CloneGallery Production Deployment Guide

This guide covers deploying CloneGallery in production with all the requested features:

- **PostgreSQL** for production database
- **GPU-enabled AI** with CPU fallback to external providers
- **MinIO/S3** storage with CDN support
- **JWT authentication** with OAuth integration
- **RBAC permissions** system
- **Advanced search** with EXIF data
- **Kubernetes** deployment with Helm charts

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   AI Service    │
│   (React/Vue)   │◄──►│   (Nginx)       │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   Redis Cache   │
                       │   (Production)  │    │   (Sessions)    │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   S3 Storage    │
                       │   (MinIO/AWS)   │
                       └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended for VPS)

```bash
# Clone the repository
git clone https://github.com/your-org/clonegallery.git
cd clonegallery

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start with PostgreSQL (production)
docker-compose up -d postgres redis
docker-compose run --rm db-migrate
docker-compose run --rm db-seed
docker-compose up -d

# Or start with MinIO for S3-compatible storage
docker-compose -f docker-compose.yml -f docker-compose.minio.yml up -d
```

### Option 2: Kubernetes (Production Scale)

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply secrets (update with your values)
kubectl apply -f k8s/secrets.yaml

# Deploy database
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml

# Deploy application
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/web-deployment.yaml

# Set up ingress
kubectl apply -f k8s/ingress.yaml
```

### Option 3: Helm Chart (Advanced)

```bash
# Add Helm repository (if published)
helm repo add clonegallery https://charts.clonegallery.com
helm repo update

# Install with custom values
helm install clonegallery clonegallery/clonegallery \
  --namespace clonegallery \
  --create-namespace \
  --values helm/clonegallery/values.yaml \
  --set config.jwtSecret="your-secret" \
  --set secrets.replicateApiToken="your-token"
```

## 🗄️ Database Configuration

### PostgreSQL (Production)

The system uses PostgreSQL for production with the following features:

- **Full-text search** with GIN indexes
- **JSONB support** for flexible metadata
- **Triggers** for automatic updates
- **UUID primary keys** for security
- **Proper indexing** for performance

#### Schema Features

```sql
-- Users with roles and permissions
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    role user_role NOT NULL DEFAULT 'Visitor',
    -- ... other fields
);

-- Images with EXIF data support
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    -- EXIF data fields
    camera_make VARCHAR(100),
    camera_model VARCHAR(100),
    focal_length REAL,
    aperture REAL,
    iso INTEGER,
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(10, 8),
    -- ... other fields
);

-- Full-text search indexes
CREATE INDEX idx_images_title_gin ON images USING gin(to_tsvector('english', title));
CREATE INDEX idx_images_caption_gin ON images USING gin(to_tsvector('english', caption));
```

#### Migration System

```bash
# Run migrations
python database/postgresql/migrate.py migrate

# Check status
python database/postgresql/migrate.py status

# Rollback (if needed)
python database/postgresql/migrate.py rollback --version 002
```

### SQLite (Development)

For local development, SQLite is still supported:

```bash
# Use development profile
docker-compose --profile development up -d
```

## 🤖 AI Generation Configuration

### GPU-Enabled (Local)

For teams with GPU access:

```yaml
# docker-compose.yml
api:
  environment:
    - AI_PROVIDER=local
    - CUDA_VISIBLE_DEVICES=0
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### CPU Fallback (External APIs)

For teams without GPU or cloud deployment:

```yaml
# docker-compose.yml
api:
  environment:
    - AI_PROVIDER=replicate
    - REPLICATE_API_TOKEN=your_token
    # OR
    - AI_PROVIDER=openai
    - OPENAI_API_KEY=your_key
```

#### Supported Providers

1. **Replicate** (Recommended)
   - Easy setup
   - Pay-per-use
   - Multiple models available

2. **OpenAI DALL-E**
   - High quality
   - Rate limited
   - More expensive

3. **Stability AI**
   - Good quality
   - Competitive pricing

## 💾 Storage Configuration

### Local Storage (Development)

```yaml
# docker-compose.yml
web:
  volumes:
    - ./uploads:/app/uploads
```

### MinIO (Local S3-Compatible)

```bash
# Start MinIO
docker-compose -f docker-compose.minio.yml up -d

# Access MinIO console
open http://localhost:9001
# Username: clonegallery
# Password: clonegallery123
```

### AWS S3 (Production)

```yaml
# Environment variables
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET=clonegallery-images
S3_THUMBNAIL_BUCKET=clonegallery-thumbnails
```

### CDN Configuration

For production, set up CloudFront or Cloudflare:

```yaml
# CloudFront distribution
Origins:
  - DomainName: your-bucket.s3.amazonaws.com
    OriginPath: /images
    CustomOriginConfig:
      HTTPPort: 443
      HTTPSPort: 443
      OriginProtocolPolicy: https-only

Behaviors:
  - PathPattern: /images/*
    TargetOriginId: S3-Origin
    ViewerProtocolPolicy: redirect-to-https
    CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad  # CachingOptimized
```

## 🔐 Authentication & Authorization

### JWT Authentication

The system uses JWT tokens for stateless authentication:

```python
# Token creation
token = create_access_token(user_id, role)

# Token verification
payload = verify_token(token)
user = get_user_by_id(payload["user_id"])
```

### OAuth Integration

#### Google OAuth

```yaml
# Environment variables
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

#### GitHub OAuth

```yaml
# Environment variables
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
```

### RBAC Permissions

The system implements role-based access control:

```python
# Permission levels
class UserRole(str, Enum):
    ADMIN = "Admin"      # Full access
    EDITOR = "Editor"    # Upload, edit, moderate
    VISITOR = "Visitor"  # View only

# Permission checks
def require_permission(permission: str):
    def decorator(func):
        def wrapper(current_user: Dict = Depends(get_current_user)):
            if not has_permission(current_user["role"], permission):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return func(current_user)
        return wrapper
    return decorator
```

## 🔍 Advanced Search Features

### Full-Text Search

```sql
-- Search images by title, caption, and tags
SELECT * FROM images 
WHERE to_tsvector('english', title || ' ' || COALESCE(caption, '')) 
@@ plainto_tsquery('english', 'search term');
```

### EXIF Data Filtering

```python
# Search by camera settings
filters = {
    "camera_make": "Canon",
    "aperture_min": 2.8,
    "aperture_max": 5.6,
    "iso_max": 1600,
    "focal_length_min": 50
}
```

### Vector Search (CLIP Embeddings)

```python
# Generate embeddings for similarity search
def generate_image_embedding(image_path: str) -> np.ndarray:
    image = Image.open(image_path)
    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)
    return image_features.numpy()

# Search similar images
def find_similar_images(query_embedding: np.ndarray, limit: int = 10):
    # Use vector similarity search
    pass
```

## 📊 Monitoring & Observability

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# AI service health
curl http://localhost:8000/health/ai
```

### Metrics

The system exposes Prometheus metrics:

- Request duration
- Database query time
- AI generation time
- Storage operations
- User activity

### Logging

Structured logging with different levels:

```python
logger.info("User registered", extra={
    "user_id": user_id,
    "email": email,
    "role": role
})
```

## 🚀 Scaling Considerations

### Horizontal Scaling

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: clonegallery-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
```

### Database Scaling

- **Read replicas** for read-heavy workloads
- **Connection pooling** with PgBouncer
- **Partitioning** for large image tables
- **Caching** with Redis

### Storage Scaling

- **CDN** for global content delivery
- **Multi-region** S3 buckets
- **Image optimization** with WebP/AVIF
- **Lazy loading** for large galleries

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL logs
   docker-compose logs postgres
   
   # Test connection
   docker-compose exec postgres psql -U clonegallery -d clonegallery
   ```

2. **AI Generation Fails**
   ```bash
   # Check API logs
   docker-compose logs api
   
   # Test AI service
   curl http://localhost:8000/models/status
   ```

3. **Storage Issues**
   ```bash
   # Check MinIO logs
   docker-compose logs minio
   
   # Test S3 connection
   aws s3 ls s3://clonegallery-images
   ```

### Performance Optimization

1. **Database Indexes**
   ```sql
   -- Add missing indexes
   CREATE INDEX CONCURRENTLY idx_images_uploaded_at ON images(uploaded_at);
   CREATE INDEX CONCURRENTLY idx_images_views ON images(views DESC);
   ```

2. **Redis Caching**
   ```python
   # Cache frequently accessed data
   @cache(expire=300)  # 5 minutes
   def get_popular_images():
       return db.query("SELECT * FROM images ORDER BY views DESC LIMIT 20")
   ```

3. **Image Optimization**
   ```python
   # Generate multiple sizes
   sizes = [(300, 300), (600, 600), (1200, 1200)]
   for size in sizes:
       thumbnail = image.thumbnail(size)
       storage.upload(thumbnail, f"thumb_{size[0]}x{size[1]}")
   ```

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Charts](https://helm.sh/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Stable Diffusion Guide](https://huggingface.co/docs/diffusers/)

## 🤝 Support

For issues and questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the [GitHub issues](https://github.com/your-org/clonegallery/issues)
3. Join our [Discord community](https://discord.gg/clonegallery)
4. Contact support at [support@clonegallery.com](mailto:support@clonegallery.com)
