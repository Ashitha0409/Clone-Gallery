-- Migration: 003_add_triggers.sql
-- Description: Add PostgreSQL triggers for automatic updates
-- Created: 2024-12-19
-- Version: 1.0.2

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to update tag counts
CREATE OR REPLACE FUNCTION update_tag_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE tags SET count = count + 1 WHERE id = NEW.tag_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE tags SET count = count - 1 WHERE id = OLD.tag_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.tag_id != NEW.tag_id THEN
            UPDATE tags SET count = count - 1 WHERE id = OLD.tag_id;
            UPDATE tags SET count = count + 1 WHERE id = NEW.tag_id;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Function to update album image count
CREATE OR REPLACE FUNCTION update_album_image_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE albums SET image_count = image_count + 1 WHERE id = NEW.album_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE albums SET image_count = image_count - 1 WHERE id = OLD.album_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.album_id != NEW.album_id THEN
            UPDATE albums SET image_count = image_count - 1 WHERE id = OLD.album_id;
            UPDATE albums SET image_count = image_count + 1 WHERE id = NEW.album_id;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Function to update user uploads count
CREATE OR REPLACE FUNCTION update_user_uploads_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE users SET uploads = uploads + 1 WHERE id = NEW.uploader_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE users SET uploads = uploads - 1 WHERE id = OLD.uploader_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.uploader_id != NEW.uploader_id THEN
            UPDATE users SET uploads = uploads - 1 WHERE id = OLD.uploader_id;
            UPDATE users SET uploads = uploads + 1 WHERE id = NEW.uploader_id;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Function to update image views
CREATE OR REPLACE FUNCTION increment_image_views()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE images SET views = views + 1 WHERE id = NEW.image_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to clean expired sessions
CREATE OR REPLACE FUNCTION clean_expired_sessions()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM user_sessions WHERE expires_at < NOW();
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Function to generate username from email
CREATE OR REPLACE FUNCTION generate_username_from_email()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.username IS NULL OR NEW.username = '' THEN
        NEW.username = split_part(NEW.email, '@', 1);
        
        -- Ensure username is unique
        WHILE EXISTS (SELECT 1 FROM users WHERE username = NEW.username AND id != NEW.id) LOOP
            NEW.username = NEW.username || '_' || floor(random() * 1000)::text;
        END LOOP;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to create slug from title
CREATE OR REPLACE FUNCTION create_slug_from_title()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.slug IS NULL OR NEW.slug = '' THEN
        NEW.slug = lower(regexp_replace(NEW.name, '[^a-zA-Z0-9]+', '-', 'g'));
        NEW.slug = trim(both '-' from NEW.slug);
        
        -- Ensure slug is unique
        WHILE EXISTS (SELECT 1 FROM tags WHERE slug = NEW.slug AND id != NEW.id) LOOP
            NEW.slug = NEW.slug || '-' || floor(random() * 1000)::text;
        END LOOP;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER generate_username_trigger
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION generate_username_from_email();

-- Apply triggers to images table
CREATE TRIGGER update_images_updated_at
    BEFORE UPDATE ON images
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_uploads_on_image_insert
    AFTER INSERT ON images
    FOR EACH ROW
    EXECUTE FUNCTION update_user_uploads_count();

CREATE TRIGGER update_user_uploads_on_image_delete
    AFTER DELETE ON images
    FOR EACH ROW
    EXECUTE FUNCTION update_user_uploads_count();

CREATE TRIGGER update_user_uploads_on_image_update
    AFTER UPDATE ON images
    FOR EACH ROW
    EXECUTE FUNCTION update_user_uploads_count();

-- Apply triggers to albums table
CREATE TRIGGER update_albums_updated_at
    BEFORE UPDATE ON albums
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply triggers to image_tags table
CREATE TRIGGER update_tag_count_on_image_tags_insert
    AFTER INSERT ON image_tags
    FOR EACH ROW
    EXECUTE FUNCTION update_tag_count();

CREATE TRIGGER update_tag_count_on_image_tags_delete
    AFTER DELETE ON image_tags
    FOR EACH ROW
    EXECUTE FUNCTION update_tag_count();

CREATE TRIGGER update_tag_count_on_image_tags_update
    AFTER UPDATE ON image_tags
    FOR EACH ROW
    EXECUTE FUNCTION update_tag_count();

-- Apply triggers to album_images table
CREATE TRIGGER update_album_image_count_on_album_images_insert
    AFTER INSERT ON album_images
    FOR EACH ROW
    EXECUTE FUNCTION update_album_image_count();

CREATE TRIGGER update_album_image_count_on_album_images_delete
    AFTER DELETE ON album_images
    FOR EACH ROW
    EXECUTE FUNCTION update_album_image_count();

CREATE TRIGGER update_album_image_count_on_album_images_update
    AFTER UPDATE ON album_images
    FOR EACH ROW
    EXECUTE FUNCTION update_album_image_count();

-- Apply triggers to user_likes table
CREATE TRIGGER increment_image_views_on_like
    AFTER INSERT ON user_likes
    FOR EACH ROW
    EXECUTE FUNCTION increment_image_views();

-- Apply triggers to comments table
CREATE TRIGGER update_comments_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Clean expired sessions periodically
CREATE TRIGGER clean_expired_sessions_trigger
    AFTER INSERT ON user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION clean_expired_sessions();

-- Apply slug generation trigger to tags
CREATE TRIGGER create_slug_trigger
    BEFORE INSERT OR UPDATE ON tags
    FOR EACH ROW
    EXECUTE FUNCTION create_slug_from_title();

-- Insert migration record
INSERT INTO migrations (version, description) VALUES ('003', 'Add PostgreSQL triggers for automatic updates');
