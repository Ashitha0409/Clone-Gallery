-- CloneGallery Database Schema
-- SQLite database for image gallery management

-- Users table
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

-- Images table
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

-- Tags table
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    count INTEGER DEFAULT 0,
    trending BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Image tags junction table
CREATE TABLE IF NOT EXISTS image_tags (
    image_id TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (image_id, tag_id),
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Albums table
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

-- Album images junction table
CREATE TABLE IF NOT EXISTS album_images (
    album_id TEXT NOT NULL,
    image_id TEXT NOT NULL,
    position INTEGER DEFAULT 0,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (album_id, image_id),
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- User likes table (one like per user per image)
CREATE TABLE IF NOT EXISTS user_likes (
    user_id TEXT NOT NULL,
    image_id TEXT NOT NULL,
    liked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, image_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- AI generation metadata table
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

-- Analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value TEXT NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_images_uploader ON images(uploader_id);
CREATE INDEX IF NOT EXISTS idx_images_uploaded_at ON images(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_images_privacy ON images(privacy);
CREATE INDEX IF NOT EXISTS idx_images_ai_generated ON images(is_ai_generated);
CREATE INDEX IF NOT EXISTS idx_user_likes_user ON user_likes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_likes_image ON user_likes(image_id);
CREATE INDEX IF NOT EXISTS idx_image_tags_image ON image_tags(image_id);
CREATE INDEX IF NOT EXISTS idx_image_tags_tag ON image_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_album_images_album ON album_images(album_id);
CREATE INDEX IF NOT EXISTS idx_album_images_image ON album_images(image_id);

-- Triggers to update timestamps
CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
    AFTER UPDATE ON users
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_images_timestamp 
    AFTER UPDATE ON images
    BEGIN
        UPDATE images SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Trigger to update tag counts when image_tags change
CREATE TRIGGER IF NOT EXISTS update_tag_count_insert
    AFTER INSERT ON image_tags
    BEGIN
        UPDATE tags SET count = count + 1 WHERE id = NEW.tag_id;
    END;

CREATE TRIGGER IF NOT EXISTS update_tag_count_delete
    AFTER DELETE ON image_tags
    BEGIN
        UPDATE tags SET count = count - 1 WHERE id = OLD.tag_id;
    END;

-- Trigger to update album image count
CREATE TRIGGER IF NOT EXISTS update_album_count_insert
    AFTER INSERT ON album_images
    BEGIN
        UPDATE albums SET image_count = image_count + 1 WHERE id = NEW.album_id;
    END;

CREATE TRIGGER IF NOT EXISTS update_album_count_delete
    AFTER DELETE ON album_images
    BEGIN
        UPDATE albums SET image_count = image_count - 1 WHERE id = OLD.album_id;
    END;

-- Trigger to update user uploads count
CREATE TRIGGER IF NOT EXISTS update_user_uploads_insert
    AFTER INSERT ON images
    BEGIN
        UPDATE users SET uploads = uploads + 1 WHERE id = NEW.uploader_id;
    END;

CREATE TRIGGER IF NOT EXISTS update_user_uploads_delete
    AFTER DELETE ON images
    BEGIN
        UPDATE users SET uploads = uploads - 1 WHERE id = OLD.uploader_id;
    END;
