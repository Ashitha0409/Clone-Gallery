# CloneGallery Deployment Guide

This guide will help you deploy the CloneGallery application with all its features including database setup, image editing, AI generation, and proper like management.

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose
- At least 4GB RAM available for Docker
- 10GB free disk space

### One-Command Deployment

**Windows:**
```bash
deploy.bat
```

**Linux/Mac:**
```bash
./deploy.sh
```

## 📋 Manual Deployment

### 1. Clone and Setup

```bash
git clone <repository-url>
cd CloneGallery
mkdir -p data models uploads
```

### 2. Start Services

```bash
docker-compose up --build -d
```

### 3. Initialize Database

```bash
# Run migrations
docker-compose run --rm db-migrate

# Seed with sample data
docker-compose run --rm db-seed

# Or use the unified management script
docker-compose exec db python /app/database/manage.py setup
```

### 4. Access the Application

- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 🎨 Features Included

### ✅ Database Setup
- SQLite database with proper schema
- User management with roles (Admin, Editor, Visitor)
- Image metadata and tagging system
- Like tracking (one like per user per image)
- AI generation metadata storage

### ✅ Image Editing
- **Crop:** Multiple aspect ratios (1:1, 4:3, 16:9, 3:2)
- **Resize:** Custom dimensions with aspect ratio preservation
- **Filters:** Grayscale, Sepia, Vintage, Brightness, Contrast
- **Adjustments:** Brightness, Contrast, Saturation sliders
- **Real-time preview** with canvas-based editing

### ✅ AI Image Generation
- Integration with Stable Diffusion API
- Multiple model support (SD 1.5, 2.1, XL)
- Customizable parameters (steps, guidance scale)
- Automatic saving to gallery
- Fallback to demo mode if API unavailable

### ✅ Like System
- One like per user per image maximum
- Visual feedback with filled/outlined heart icons
- Real-time like count updates
- Persistent like state management

### ✅ Responsive Design
- Mobile-first approach
- Dynamic theme switching (light/dark)
- Consistent color scheme throughout
- Touch-friendly interface

## 🗄️ Database Schema

The application uses SQLite with a comprehensive schema including:

### Core Tables
- **users:** User accounts with roles and statistics
- **images:** Image metadata and file information
- **user_likes:** One-to-one like relationships
- **tags:** Categorization system
- **albums:** Image collections
- **ai_generation_meta:** AI generation parameters

### Management Tables
- **migrations:** Database migration tracking
- **seeders:** Database seeder tracking
- **analytics:** Application metrics

### Database Management
- **Migration System:** Version-controlled schema changes
- **Seeder System:** Sample data management
- **Backup/Restore:** Data protection tools
- **Health Checks:** Service monitoring

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_PATH=/app/data/clonegallery.db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# AI Models
MODEL_CACHE_DIR=/app/models
CUDA_VISIBLE_DEVICES=0
```

### Docker Services

- **web:** Nginx frontend server
- **api:** FastAPI backend with AI models
- **redis:** Caching and job queue
- **db:** SQLite database service with migrations and seeding
- **db-migrate:** Database migration service (runs once)
- **db-seed:** Database seeder service (runs once)
- **db-reset:** Database reset service (runs once)

## 📊 Demo Accounts

| Role | Email | Password | Features |
|------|-------|----------|----------|
| Admin | admin@clonegallery.local | - | Full access, AI generation |
| Editor | editor@clonegallery.local | - | Upload, edit, manage content |
| Visitor | user@clonegallery.local | - | View, like, search |

## 🛠️ Management Commands

```bash
# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Update and restart
docker-compose pull && docker-compose up -d

# Access database
docker-compose exec db sqlite3 /app/data/clonegallery.db

# Check database status
docker-compose exec db python /app/database/manage.py status

# Run migrations
docker-compose run --rm db-migrate

# Seed database
docker-compose run --rm db-seed

# Reset database
docker-compose run --rm db-reset
```

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts:** Ensure ports 3000 and 8000 are available
2. **Memory issues:** Increase Docker memory limit to 4GB+
3. **AI generation fails:** Check if GPU drivers are installed for CUDA support
4. **Database errors:** Run `docker-compose run --rm db-init` to reinitialize

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs api
docker-compose logs redis
```

### Reset Everything

```bash
docker-compose down -v
docker system prune -f
./deploy.sh  # or deploy.bat on Windows
```

## 🚀 Production Deployment

For production deployment, consider:

1. **Use PostgreSQL** instead of SQLite
2. **Set up SSL certificates** for HTTPS
3. **Configure proper secrets management**
4. **Set up monitoring and logging**
5. **Use a reverse proxy** like Traefik or Nginx
6. **Implement backup strategies**

## 📈 Performance

- **Frontend:** Optimized with gzip compression and caching
- **Backend:** Async FastAPI with Redis caching
- **Database:** Indexed queries for fast search
- **Images:** Lazy loading and responsive thumbnails

## 🔒 Security

- CORS properly configured
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure file upload handling
- SQL injection prevention

## 📝 API Endpoints

- `GET /health` - Health check
- `POST /api/generate/image` - AI image generation
- `POST /api/embed/text` - Text embedding
- `POST /api/embed/image` - Image embedding
- `GET /api/models/status` - Model status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
