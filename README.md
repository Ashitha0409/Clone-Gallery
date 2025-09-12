# CloneGallery — AI-Enhanced Responsive Image Gallery Platform

[![Build Status](https://img.shields.io/github/workflow/status/username/clonegallery/CI)](https://github.com/username/clonegallery/actions)
[![Coverage](https://img.shields.io/codecov/c/github/username/clonegallery)](https://codecov.io/gh/username/clonegallery)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready image gallery platform with AI-powered features, vector search, responsive image delivery, and comprehensive role-based access control.

## 🚀 Quick Start

Get CloneGallery running locally with one command:

```bash
git clone https://github.com/username/clonegallery.git
cd clonegallery
chmod +x start.sh
./start.sh
```

**That's it!** The script will:
- Set up all services (Laravel, PostgreSQL, Redis, MinIO, Milvus, AI)
- Run database migrations and seed demo data
- Configure storage and vector search
- Start the application at http://localhost

### Default Admin Credentials
- **Email**: admin@clonegallery.local
- **Password**: admin123

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Functionality
- **Multi-format Upload**: JPEG, PNG, GIF, WebP, AVIF with chunked upload support
- **Responsive Images**: Automatic generation of optimized sizes (AVIF/WebP/JPEG fallbacks)
- **Album Management**: Organize images into collections with drag-and-drop ordering
- **Advanced Search**: Full-text search + AI-powered semantic vector search
- **Real-time Updates**: WebSocket notifications for upload progress and processing

### AI & ML Features
- **Vector Search**: CLIP-based semantic similarity search for images and text
- **AI Generation**: Optional Stable Diffusion integration for image creation
- **Smart Tagging**: Automatic tag suggestions based on image content
- **Duplicate Detection**: Perceptual hashing to identify similar images

### Security & Access Control
- **Role-Based Access Control (RBAC)**: Admin, Editor, Visitor roles with granular permissions
- **JWT Authentication**: Laravel Sanctum for stateless API authentication
- **Privacy Controls**: Public, unlisted, and private image sharing options
- **Audit Logging**: Complete activity trail for compliance and debugging

### Performance & Scalability
- **Redis Caching**: Session management, query caching, and job queues
- **Background Processing**: Asynchronous image processing and AI operations
- **CDN-Ready**: Optimized for content delivery networks
- **Horizontal Scaling**: Microservices architecture supports multi-instance deployment

### Developer Experience
- **OpenAPI 3.0**: Complete API documentation with interactive playground
- **Docker Compose**: One-command local development environment
- **Comprehensive Tests**: Unit, integration, and E2E tests with 90%+ coverage
- **CI/CD Ready**: GitHub Actions workflows for testing and deployment

## 🏗 Architecture

### Services Overview

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│    nginx    │────│ Laravel App  │────│ PostgreSQL  │
│  (web/ssl)  │    │   (API/UI)   │    │ (pgvector)  │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
   ┌───────────┐    ┌─────────────┐   ┌─────────────┐
   │   Redis   │    │    MinIO    │   │   Milvus    │
   │(cache/queue)│   │ (S3 storage)│   │ (vectors)   │
   └───────────┘    └─────────────┘   └─────────────┘
         │
   ┌───────────┐    ┌─────────────┐   ┌─────────────┐
   │  Worker   │    │ WebSocket   │   │ AI Generator│
   │(background)│   │ (realtime)  │   │ (optional)  │
   └───────────┘    └─────────────┘   └─────────────┘
```

### Key Technologies
- **Backend**: Laravel 10 with Sanctum authentication
- **Database**: PostgreSQL with pgvector extension for embeddings
- **Cache**: Redis for sessions, caching, and job queues
- **Storage**: MinIO S3-compatible object storage
- **Vector DB**: Milvus for similarity search and AI features
- **AI/ML**: CLIP embeddings, Stable Diffusion (via Replicate or local)
- **Frontend**: Alpine.js with responsive design and WebSocket integration
- **Testing**: Cypress E2E, PHPUnit, Jest with comprehensive coverage

## 📋 Requirements

### System Requirements
- **Docker & Docker Compose**: Latest versions
- **Memory**: 4GB+ RAM (8GB+ recommended with AI features)
- **Storage**: 10GB+ available disk space
- **Network**: Internet connection for AI services (if using Replicate/OpenAI)

### Optional GPU Support
For local AI image generation:
- **NVIDIA GPU**: CUDA-compatible with 4GB+ VRAM
- **NVIDIA Container Toolkit**: For Docker GPU access

## 🛠 Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/username/clonegallery.git
   cd clonegallery
   ```

2. **Run the setup script**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

3. **Access the application**
   - Web UI: http://localhost
   - API Documentation: http://localhost/api/docs
   - MinIO Console: http://localhost:9001
   - Milvus Console: http://localhost:9091

### Manual Setup

If you prefer to set up services manually:

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

2. **Start core services**
   ```bash
   docker compose up -d db cache storage
   ```

3. **Run migrations and build**
   ```bash
   docker compose exec app php artisan migrate
   docker compose exec app php artisan db:seed
   ```

4. **Start all services**
   ```bash
   docker compose up -d
   ```

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Application
APP_URL=http://localhost
APP_DEBUG=false

# Database
DB_PASSWORD=your-secure-password

# AI Services (choose one)
AI_PROVIDER=replicate  # or 'local' or 'openai'
REPLICATE_API_TOKEN=your-token
OPENAI_API_KEY=your-key

# Storage
MINIO_ROOT_USER=clonegallery
MINIO_ROOT_PASSWORD=your-secure-password

# Performance
CACHE_DRIVER=redis
QUEUE_CONNECTION=redis
```

### AI Provider Configuration

#### Replicate (Recommended)
```env
AI_PROVIDER=replicate
REPLICATE_API_TOKEN=r8_your_token_here
```

#### OpenAI
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your_key_here
```

#### Local AI (GPU Required)
```bash
# Enable GPU profile
docker compose --profile gpu up -d
```

## 📖 Usage

### Image Upload

**Via Web Interface:**
1. Navigate to the gallery
2. Drag and drop images or click to select
3. Add metadata (title, caption, alt text, tags)
4. Set privacy level
5. Upload and wait for processing

**Via API:**
```bash
# Initialize upload
curl -X POST http://localhost/api/uploads/init \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename":"image.jpg","mime_type":"image/jpeg","size":1048576}'

# Upload chunks
curl -X PUT http://localhost/api/uploads/{uploadId}/chunks/0 \
  -H "Authorization: Bearer $TOKEN" \
  -F "chunk=@image_chunk_0"

# Complete upload
curl -X POST http://localhost/api/uploads/{uploadId}/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Image","caption":"Description","privacy":"public"}'
```

### Search

**Text Search:**
```javascript
// Full-text search
fetch('/api/search/text', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({q: 'mountain landscape'})
})
```

**Vector Search:**
```javascript
// Semantic similarity search
fetch('/api/search/vector', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    type: 'text',
    query_text: 'beautiful nature scenery',
    k: 20
  })
})
```

### Role Management

**Create Role:**
```bash
curl -X POST http://localhost/api/admin/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Photographer",
    "permissions": ["upload", "edit_own", "view_analytics"]
  }'
```

## 📚 API Reference

### Authentication

All API endpoints require authentication via Bearer token:

```bash
# Login
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer $TOKEN" http://localhost/api/images
```

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/images` | List images with filters |
| POST | `/api/uploads/init` | Initialize chunked upload |
| PUT | `/api/uploads/{id}/chunks/{n}` | Upload chunk |
| POST | `/api/uploads/{id}/complete` | Complete upload |
| GET | `/api/images/{id}` | Get image details |
| PATCH | `/api/images/{id}` | Update image metadata |
| DELETE | `/api/images/{id}` | Delete image |
| POST | `/api/search/text` | Full-text search |
| POST | `/api/search/vector` | Vector similarity search |

For complete API documentation, visit `/api/docs` when running locally.

## 🧪 Testing

### Running Tests

**All Tests:**
```bash
# Run full test suite
docker compose exec app php artisan test
npm test
```

**Unit Tests:**
```bash
# Laravel/PHP unit tests
docker compose exec app php artisan test --testsuite=Unit

# JavaScript unit tests  
npm run test:unit
```

**Integration Tests:**
```bash
docker compose exec app php artisan test --testsuite=Feature
```

**End-to-End Tests:**
```bash
# Headless mode
npm run test

# Interactive mode
npm run test:open
```

**Performance/Accessibility:**
```bash
# Lighthouse audits
npm run lighthouse:desktop
npm run lighthouse:mobile

# Accessibility testing
npm run cypress:run -- --spec "cypress/e2e/accessibility.cy.js"
```

### Test Coverage

Current test coverage:
- **Unit Tests**: 85%+ coverage
- **Integration Tests**: 70%+ coverage  
- **E2E Tests**: Critical user flows covered
- **Performance**: Lighthouse scores 90+ for performance and accessibility

### Writing Tests

**Unit Test Example:**
```php
<?php
// tests/Unit/ImageProcessingTest.php
public function test_image_resize_maintains_aspect_ratio()
{
    $service = new ImageProcessingService();
    $result = $service->resizeImage('/path/to/image.jpg', 800, null, 'webp');
    
    $this->assertFileExists($result);
    [$width, $height] = getimagesize($result);
    $this->assertEquals(800, $width);
}
```

**E2E Test Example:**
```javascript
// cypress/e2e/upload.cy.js
describe('Image Upload', () => {
  it('successfully uploads and processes image', () => {
    cy.login('user@example.com', 'password')
    cy.uploadImage('test-image.jpg')
    cy.get('[data-cy="processing-status"]').should('contain', 'complete')
    cy.get('[data-cy="image-grid"]').should('contain', 'test-image')
  })
})
```

## 🚀 Deployment

### VPS Deployment

**Single Server Setup:**
```bash
# Clone on server
git clone https://github.com/username/clonegallery.git
cd clonegallery

# Configure production environment
cp .env.example .env
# Edit .env with production values

# Deploy
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**With SSL/TLS:**
```bash
# Use Traefik for automatic SSL
docker compose -f docker-compose.yml -f docker-compose.traefik.yml up -d
```

### Kubernetes Deployment

**Deploy to Kubernetes:**
```bash
# Install with Helm
helm install clonegallery ./kubernetes/helm-chart \
  --set ingress.host=gallery.yourdomain.com \
  --set ai.enabled=true \
  --set postgresql.auth.password=secure-password
```

**Scale services:**
```bash
kubectl scale deployment clonegallery-app --replicas=3
kubectl scale deployment clonegallery-worker --replicas=5
```

### Cloud Deployment

**AWS ECS:**
```bash
# Deploy using provided CloudFormation template
aws cloudformation deploy \
  --template-file aws/ecs-cluster.yml \
  --stack-name clonegallery \
  --parameter-overrides DomainName=gallery.yourdomain.com
```

**Google Cloud Run:**
```bash
# Deploy with Cloud Build
gcloud builds submit --config cloudbuild.yaml
gcloud run deploy clonegallery --image gcr.io/PROJECT/clonegallery
```

### Production Checklist

- [ ] Update all default passwords
- [ ] Configure SSL certificates
- [ ] Set up database backups
- [ ] Configure log aggregation
- [ ] Set up monitoring and alerts
- [ ] Configure CDN for image delivery
- [ ] Test disaster recovery procedures
- [ ] Review security settings
- [ ] Configure firewall rules
- [ ] Set up CI/CD pipeline

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `npm test && composer test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to your branch: `git push origin feature/amazing-feature`
7. Submit a pull request

### Code Style

- **PHP**: Follow PSR-12 standards
- **JavaScript**: Use Prettier and ESLint configurations
- **Commit Messages**: Follow conventional commits format

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full documentation](https://clonegallery.dev/docs)
- **Issues**: [GitHub Issues](https://github.com/username/clonegallery/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/clonegallery/discussions)
- **Discord**: [Join our community](https://discord.gg/clonegallery)

## 📈 Roadmap

- [ ] **Q1 2025**: Mobile app (React Native)
- [ ] **Q2 2025**: Advanced AI features (style transfer, upscaling)
- [ ] **Q3 2025**: Plugin system for custom integrations
- [ ] **Q4 2025**: Enterprise features (SSO, advanced analytics)

---

Built with ❤️ by the CloneGallery team