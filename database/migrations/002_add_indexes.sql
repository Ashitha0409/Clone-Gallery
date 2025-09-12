-- Migration: 002_add_indexes.sql
-- Description: Add performance indexes
-- Created: 2024-12-19
-- Version: 1.0.1

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
CREATE INDEX IF NOT EXISTS idx_ai_generation_image ON ai_generation_meta(image_id);
CREATE INDEX IF NOT EXISTS idx_analytics_metric ON analytics(metric_name);
CREATE INDEX IF NOT EXISTS idx_analytics_recorded_at ON analytics(recorded_at);

-- Insert migration record
INSERT INTO migrations (version, description) VALUES ('002', 'Add performance indexes');
