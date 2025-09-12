-- Seeder: 005_albums_seeder.sql
-- Description: Seed albums table with sample collections
-- Created: 2024-12-19

-- Insert sample albums
INSERT OR IGNORE INTO albums (id, title, description, cover_image_id, created_by, created_at, privacy) VALUES
('album-001', 'Nature Collection', 'Curated collection of stunning nature photography from around the world', 'img-001', 'admin-001', '2024-09-01T10:00:00Z', 'public'),
('album-002', 'AI Experiments', 'Generated artwork and AI-assisted creative explorations', 'img-003', 'admin-001', '2024-09-02T14:30:00Z', 'public'),
('album-003', 'Urban Photography', 'Architecture and city life captured in stunning detail', 'img-002', 'editor-001', '2024-09-03T16:20:00Z', 'public'),
('album-004', 'Landscape Masterpieces', 'Breathtaking landscapes from mountains to deserts', 'img-005', 'editor-002', '2024-09-04T09:15:00Z', 'public'),
('album-005', 'Macro World', 'Close-up photography revealing hidden details', 'img-004', 'editor-001', '2024-09-05T11:30:00Z', 'public'),
('album-006', 'Night Photography', 'Urban and natural scenes captured after dark', 'img-006', 'admin-002', '2024-09-06T18:45:00Z', 'public');

-- Insert album images
INSERT OR IGNORE INTO album_images (album_id, image_id, position) VALUES
-- Nature Collection
('album-001', 'img-001', 0),
('album-001', 'img-004', 1),
('album-001', 'img-005', 2),
('album-001', 'img-008', 3),

-- AI Experiments
('album-002', 'img-003', 0),
('album-002', 'img-007', 1),

-- Urban Photography
('album-003', 'img-002', 0),
('album-003', 'img-006', 1),

-- Landscape Masterpieces
('album-004', 'img-001', 0),
('album-004', 'img-005', 1),
('album-004', 'img-008', 2),

-- Macro World
('album-005', 'img-004', 0),

-- Night Photography
('album-006', 'img-006', 0);
