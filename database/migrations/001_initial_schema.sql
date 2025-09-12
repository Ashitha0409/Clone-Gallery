-- Migration: 001_initial_schema.sql
-- Description: Initial database schema creation
-- Created: 2024-12-19
-- Version: 1.0.0

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('Admin', 'Editor', 'Visitor')),
    avatar TEXT,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    uploads INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create images table
CREATE TABLE IF NOT EXISTS images (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    caption TEXT,
    alt_text TEXT,
    url TEXT NOT NULL,
    thumbnail TEXT NOT NULL,
    uploader_id TEXT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    privacy TEXT DEFAULT 'public' CHECK (privacy IN ('public', 'private')),
    views INTEGER DEFAULT 0,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    width INTEGER,
    height INTEGER,
    size TEXT,
    format TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create tags table
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    count INTEGER DEFAULT 0,
    trending BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create image tags junction table
CREATE TABLE IF NOT EXISTS image_tags (
    image_id TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (image_id, tag_id),
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Create albums table
CREATE TABLE IF NOT EXISTS albums (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    cover_image_id TEXT,
    created_by TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    privacy TEXT DEFAULT 'public' CHECK (privacy IN ('public', 'private')),
    image_count INTEGER DEFAULT 0,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (cover_image_id) REFERENCES images(id) ON DELETE SET NULL
);

-- Create album images junction table
CREATE TABLE IF NOT EXISTS album_images (
    album_id TEXT NOT NULL,
    image_id TEXT NOT NULL,
    position INTEGER DEFAULT 0,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (album_id, image_id),
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- Create user likes table (one like per user per image)
CREATE TABLE IF NOT EXISTS user_likes (
    user_id TEXT NOT NULL,
    image_id TEXT NOT NULL,
    liked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, image_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- Create AI generation metadata table
CREATE TABLE IF NOT EXISTS ai_generation_meta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt TEXT NOT NULL,
    negative_prompt TEXT,
    steps INTEGER,
    guidance_scale REAL,
    seed INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- Create analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value TEXT NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create migration tracking table
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    description TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert migration record
INSERT INTO migrations (version, description) VALUES ('001', 'Initial database schema creation');
