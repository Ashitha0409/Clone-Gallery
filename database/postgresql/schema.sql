-- PostgreSQL Schema for CloneGallery Production
-- This schema is optimized for production use with proper indexing and constraints

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create custom types
CREATE TYPE user_role AS ENUM ('Admin', 'Editor', 'Visitor');
CREATE TYPE privacy_level AS ENUM ('public', 'private');
CREATE TYPE image_format AS ENUM ('JPEG', 'PNG', 'GIF', 'WebP', 'AVIF', 'TIFF');

-- Users table with enhanced security
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'Visitor',
    avatar TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    uploads INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Images table with EXIF data support
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    caption TEXT,
    alt_text TEXT,
    url TEXT NOT NULL,
    thumbnail TEXT NOT NULL,
    uploader_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    privacy privacy_level DEFAULT 'public',
    views INTEGER DEFAULT 0,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    width INTEGER,
    height INTEGER,
    size_bytes BIGINT,
    format image_format,
    file_path TEXT,
    storage_provider VARCHAR(50) DEFAULT 'local', -- 'local', 's3', 'minio'
    storage_key TEXT,
    
    -- EXIF data
    camera_make VARCHAR(100),
    camera_model VARCHAR(100),
    lens_model VARCHAR(100),
    focal_length REAL,
    aperture REAL,
    shutter_speed VARCHAR(20),
    iso INTEGER,
    flash BOOLEAN,
    white_balance VARCHAR(50),
    exposure_mode VARCHAR(50),
    metering_mode VARCHAR(50),
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(10, 8),
    gps_altitude REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tags table with full-text search support
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    count INTEGER DEFAULT 0,
    trending BOOLEAN DEFAULT FALSE,
    color VARCHAR(7), -- Hex color code
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Image tags junction table
CREATE TABLE image_tags (
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (image_id, tag_id)
);

-- Albums table
CREATE TABLE albums (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    cover_image_id UUID REFERENCES images(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    privacy privacy_level DEFAULT 'public',
    image_count INTEGER DEFAULT 0,
    color_theme VARCHAR(7), -- Hex color for album theme
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Album images junction table with ordering
CREATE TABLE album_images (
    album_id UUID NOT NULL REFERENCES albums(id) ON DELETE CASCADE,
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    position INTEGER DEFAULT 0,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (album_id, image_id)
);

-- User likes table (one like per user per image)
CREATE TABLE user_likes (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    liked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, image_id)
);

-- Comments system
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    is_approved BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI generation metadata table
CREATE TABLE ai_generation_meta (
    id SERIAL PRIMARY KEY,
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'local', 'replicate', 'openai', 'stability'
    model VARCHAR(100) NOT NULL,
    prompt TEXT NOT NULL,
    negative_prompt TEXT,
    steps INTEGER,
    guidance_scale REAL,
    seed INTEGER,
    width INTEGER,
    height INTEGER,
    generation_time_ms INTEGER,
    cost_usd DECIMAL(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics table
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value TEXT NOT NULL,
    metric_type VARCHAR(50) DEFAULT 'counter', -- 'counter', 'gauge', 'histogram'
    tags JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User sessions for JWT management
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- OAuth providers
CREATE TABLE oauth_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    client_secret VARCHAR(255) NOT NULL,
    auth_url TEXT NOT NULL,
    token_url TEXT NOT NULL,
    user_info_url TEXT NOT NULL,
    scope VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- OAuth user accounts
CREATE TABLE oauth_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_id INTEGER NOT NULL REFERENCES oauth_providers(id) ON DELETE CASCADE,
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(provider_id, provider_user_id)
);

-- Vector embeddings for similarity search
CREATE TABLE image_embeddings (
    id SERIAL PRIMARY KEY,
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    embedding VECTOR(512), -- Using pgvector extension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Migration tracking
CREATE TABLE migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seeder tracking
CREATE TABLE seeders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
