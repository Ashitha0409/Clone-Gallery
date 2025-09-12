-- Seeder: 002_tags_seeder.sql
-- Description: Seed tags table with popular categories
-- Created: 2024-12-19

-- Insert popular tags
INSERT OR IGNORE INTO tags (name, count, trending) VALUES
('nature', 124, 1),
('landscape', 89, 1),
('architecture', 67, 0),
('AI', 45, 1),
('urban', 56, 0),
('abstract', 34, 0),
('mountains', 78, 1),
('ocean', 92, 0),
('sunset', 65, 1),
('portrait', 43, 0),
('macro', 28, 0),
('black-and-white', 31, 0),
('street', 39, 0),
('wildlife', 52, 1),
('travel', 87, 1),
('minimalist', 23, 0),
('vintage', 41, 0),
('modern', 58, 0),
('artistic', 36, 0),
('photography', 156, 1);
