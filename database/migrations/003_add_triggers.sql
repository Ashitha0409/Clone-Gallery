-- Migration: 003_add_triggers.sql
-- Description: Add database triggers for automatic updates
-- Created: 2024-12-19
-- Version: 1.0.2

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

-- Insert migration record
INSERT INTO migrations (version, description) VALUES ('003', 'Add database triggers for automatic updates');
