-- PostgreSQL Indexes for CloneGallery
-- Optimized for production performance

-- Users table indexes
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_username ON users(username);
CREATE INDEX CONCURRENTLY idx_users_role ON users(role);
CREATE INDEX CONCURRENTLY idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_users_joined_at ON users(joined_at);

-- Images table indexes
CREATE INDEX CONCURRENTLY idx_images_uploader ON images(uploader_id);
CREATE INDEX CONCURRENTLY idx_images_uploaded_at ON images(uploaded_at);
CREATE INDEX CONCURRENTLY idx_images_privacy ON images(privacy);
CREATE INDEX CONCURRENTLY idx_images_ai_generated ON images(is_ai_generated);
CREATE INDEX CONCURRENTLY idx_images_views ON images(views DESC);
CREATE INDEX CONCURRENTLY idx_images_format ON images(format);
CREATE INDEX CONCURRENTLY idx_images_storage_provider ON images(storage_provider);
CREATE INDEX CONCURRENTLY idx_images_storage_key ON images(storage_key);

-- Full-text search indexes
CREATE INDEX CONCURRENTLY idx_images_title_gin ON images USING gin(to_tsvector('english', title));
CREATE INDEX CONCURRENTLY idx_images_caption_gin ON images USING gin(to_tsvector('english', caption));
CREATE INDEX CONCURRENTLY idx_images_alt_text_gin ON images USING gin(to_tsvector('english', alt_text));

-- EXIF data indexes
CREATE INDEX CONCURRENTLY idx_images_camera_make ON images(camera_make);
CREATE INDEX CONCURRENTLY idx_images_camera_model ON images(camera_model);
CREATE INDEX CONCURRENTLY idx_images_focal_length ON images(focal_length);
CREATE INDEX CONCURRENTLY idx_images_aperture ON images(aperture);
CREATE INDEX CONCURRENTLY idx_images_iso ON images(iso);
CREATE INDEX CONCURRENTLY idx_images_gps ON images(gps_latitude, gps_longitude) WHERE gps_latitude IS NOT NULL;

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY idx_images_uploader_privacy ON images(uploader_id, privacy);
CREATE INDEX CONCURRENTLY idx_images_uploaded_privacy ON images(uploaded_at DESC, privacy);
CREATE INDEX CONCURRENTLY idx_images_ai_privacy ON images(is_ai_generated, privacy);

-- Tags table indexes
CREATE INDEX CONCURRENTLY idx_tags_name ON tags(name);
CREATE INDEX CONCURRENTLY idx_tags_slug ON tags(slug);
CREATE INDEX CONCURRENTLY idx_tags_trending ON tags(trending) WHERE trending = true;
CREATE INDEX CONCURRENTLY idx_tags_count ON tags(count DESC);

-- Full-text search for tags
CREATE INDEX CONCURRENTLY idx_tags_name_gin ON tags USING gin(to_tsvector('english', name));
CREATE INDEX CONCURRENTLY idx_tags_description_gin ON tags USING gin(to_tsvector('english', description));

-- Image tags junction table indexes
CREATE INDEX CONCURRENTLY idx_image_tags_image ON image_tags(image_id);
CREATE INDEX CONCURRENTLY idx_image_tags_tag ON image_tags(tag_id);
CREATE INDEX CONCURRENTLY idx_image_tags_created ON image_tags(created_at);

-- Albums table indexes
CREATE INDEX CONCURRENTLY idx_albums_created_by ON albums(created_by);
CREATE INDEX CONCURRENTLY idx_albums_privacy ON albums(privacy);
CREATE INDEX CONCURRENTLY idx_albums_created_at ON albums(created_at);
CREATE INDEX CONCURRENTLY idx_albums_cover_image ON albums(cover_image_id);

-- Full-text search for albums
CREATE INDEX CONCURRENTLY idx_albums_title_gin ON albums USING gin(to_tsvector('english', title));
CREATE INDEX CONCURRENTLY idx_albums_description_gin ON albums USING gin(to_tsvector('english', description));

-- Album images junction table indexes
CREATE INDEX CONCURRENTLY idx_album_images_album ON album_images(album_id);
CREATE INDEX CONCURRENTLY idx_album_images_image ON album_images(image_id);
CREATE INDEX CONCURRENTLY idx_album_images_position ON album_images(album_id, position);

-- User likes indexes
CREATE INDEX CONCURRENTLY idx_user_likes_user ON user_likes(user_id);
CREATE INDEX CONCURRENTLY idx_user_likes_image ON user_likes(image_id);
CREATE INDEX CONCURRENTLY idx_user_likes_liked_at ON user_likes(liked_at);

-- Comments indexes
CREATE INDEX CONCURRENTLY idx_comments_image ON comments(image_id);
CREATE INDEX CONCURRENTLY idx_comments_user ON comments(user_id);
CREATE INDEX CONCURRENTLY idx_comments_parent ON comments(parent_id);
CREATE INDEX CONCURRENTLY idx_comments_approved ON comments(is_approved) WHERE is_approved = true;
CREATE INDEX CONCURRENTLY idx_comments_created_at ON comments(created_at);

-- Full-text search for comments
CREATE INDEX CONCURRENTLY idx_comments_content_gin ON comments USING gin(to_tsvector('english', content));

-- AI generation metadata indexes
CREATE INDEX CONCURRENTLY idx_ai_generation_image ON ai_generation_meta(image_id);
CREATE INDEX CONCURRENTLY idx_ai_generation_provider ON ai_generation_meta(provider);
CREATE INDEX CONCURRENTLY idx_ai_generation_model ON ai_generation_meta(model);
CREATE INDEX CONCURRENTLY idx_ai_generation_created_at ON ai_generation_meta(created_at);

-- Analytics indexes
CREATE INDEX CONCURRENTLY idx_analytics_metric_name ON analytics(metric_name);
CREATE INDEX CONCURRENTLY idx_analytics_recorded_at ON analytics(recorded_at);
CREATE INDEX CONCURRENTLY idx_analytics_metric_type ON analytics(metric_type);
CREATE INDEX CONCURRENTLY idx_analytics_tags ON analytics USING gin(tags);

-- User sessions indexes
CREATE INDEX CONCURRENTLY idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX CONCURRENTLY idx_user_sessions_token_hash ON user_sessions(token_hash);
CREATE INDEX CONCURRENTLY idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX CONCURRENTLY idx_user_sessions_active ON user_sessions(expires_at) WHERE expires_at > NOW();

-- OAuth providers indexes
CREATE INDEX CONCURRENTLY idx_oauth_providers_name ON oauth_providers(name);
CREATE INDEX CONCURRENTLY idx_oauth_providers_active ON oauth_providers(is_active) WHERE is_active = true;

-- OAuth accounts indexes
CREATE INDEX CONCURRENTLY idx_oauth_accounts_user ON oauth_accounts(user_id);
CREATE INDEX CONCURRENTLY idx_oauth_accounts_provider ON oauth_accounts(provider_id);
CREATE INDEX CONCURRENTLY idx_oauth_accounts_provider_user ON oauth_accounts(provider_id, provider_user_id);

-- Vector embeddings indexes
CREATE INDEX CONCURRENTLY idx_image_embeddings_image ON image_embeddings(image_id);
CREATE INDEX CONCURRENTLY idx_image_embeddings_model ON image_embeddings(model_name);
-- Vector similarity index (requires pgvector extension)
-- CREATE INDEX CONCURRENTLY idx_image_embeddings_vector ON image_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Migration and seeder tracking indexes
CREATE INDEX CONCURRENTLY idx_migrations_version ON migrations(version);
CREATE INDEX CONCURRENTLY idx_seeders_name ON seeders(name);

-- Partial indexes for performance
CREATE INDEX CONCURRENTLY idx_images_public_recent ON images(uploaded_at DESC) WHERE privacy = 'public';
CREATE INDEX CONCURRENTLY idx_images_public_popular ON images(views DESC) WHERE privacy = 'public';
CREATE INDEX CONCURRENTLY idx_images_ai_recent ON images(uploaded_at DESC) WHERE is_ai_generated = true;
CREATE INDEX CONCURRENTLY idx_users_active_recent ON users(joined_at DESC) WHERE is_active = true;
