#!/bin/bash
set -e

echo "🚀 Starting CloneGallery setup..."

# Check if .env exists, if not copy from .env.example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual configuration values!"
fi

# Generate secure passwords if they don't exist
if ! grep -q "your-secure-db-password" .env; then
    DB_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    MINIO_PASSWORD=$(openssl rand -base64 32)

    sed -i "s/your-secure-db-password/$DB_PASSWORD/g" .env
    sed -i "s/your-secure-redis-password/$REDIS_PASSWORD/g" .env
    sed -i "s/your-secure-minio-password/$MINIO_PASSWORD/g" .env

    echo "🔐 Generated secure passwords"
fi

echo "🏗️  Building and starting containers..."
docker compose up --build -d

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🗄️  Running database migrations..."
docker compose exec app php artisan migrate --force

echo "🌱 Seeding database with demo data..."
docker compose exec app php artisan db:seed --force

echo "🔗 Creating storage symbolic link..."
docker compose exec app php artisan storage:link

echo "🔧 Setting up MinIO buckets..."
docker compose exec storage mc config host add myminio http://localhost:9000 clonegallery clonegallery123
docker compose exec storage mc mb myminio/images
docker compose exec storage mc policy set public myminio/images

echo "🤖 Setting up Milvus vector database..."
docker compose exec app php artisan vector:setup

echo "✅ CloneGallery setup complete!"
echo ""
echo "🌐 Access your application:"
echo "   - Web UI: http://localhost"
echo "   - MinIO Console: http://localhost:9001"
echo "   - Milvus Console: http://localhost:9091"
echo ""
echo "👤 Default admin credentials:"
echo "   - Email: admin@clonegallery.local"
echo "   - Password: admin123"
echo ""
echo "📚 Next steps:"
echo "   1. Update .env with your API keys (Replicate, OpenAI)"
echo "   2. Configure your domain and SSL certificates"
echo "   3. Customize the application settings"
