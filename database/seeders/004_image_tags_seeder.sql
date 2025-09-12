-- Seeder: 004_image_tags_seeder.sql
-- Description: Seed image_tags junction table
-- Created: 2024-12-19

-- Link images with tags
INSERT OR IGNORE INTO image_tags (image_id, tag_id) VALUES
-- img-001: Mountain Lake Sunset
('img-001', (SELECT id FROM tags WHERE name = 'nature')),
('img-001', (SELECT id FROM tags WHERE name = 'landscape')),
('img-001', (SELECT id FROM tags WHERE name = 'sunset')),
('img-001', (SELECT id FROM tags WHERE name = 'mountains')),
('img-001', (SELECT id FROM tags WHERE name = 'photography')),

-- img-002: Urban Architecture Dreams
('img-002', (SELECT id FROM tags WHERE name = 'architecture')),
('img-002', (SELECT id FROM tags WHERE name = 'urban')),
('img-002', (SELECT id FROM tags WHERE name = 'modern')),
('img-002', (SELECT id FROM tags WHERE name = 'abstract')),

-- img-003: AI Generated Forest
('img-003', (SELECT id FROM tags WHERE name = 'AI')),
('img-003', (SELECT id FROM tags WHERE name = 'nature')),
('img-003', (SELECT id FROM tags WHERE name = 'artistic')),
('img-003', (SELECT id FROM tags WHERE name = 'photography')),

-- img-004: Ocean Waves Macro
('img-004', (SELECT id FROM tags WHERE name = 'ocean')),
('img-004', (SELECT id FROM tags WHERE name = 'macro')),
('img-004', (SELECT id FROM tags WHERE name = 'abstract')),
('img-004', (SELECT id FROM tags WHERE name = 'nature')),

-- img-005: Desert Dunes Landscape
('img-005', (SELECT id FROM tags WHERE name = 'landscape')),
('img-005', (SELECT id FROM tags WHERE name = 'nature')),
('img-005', (SELECT id FROM tags WHERE name = 'minimalist')),
('img-005', (SELECT id FROM tags WHERE name = 'photography')),

-- img-006: City Night Lights
('img-006', (SELECT id FROM tags WHERE name = 'urban')),
('img-006', (SELECT id FROM tags WHERE name = 'architecture')),
('img-006', (SELECT id FROM tags WHERE name = 'street')),
('img-006', (SELECT id FROM tags WHERE name = 'modern')),

-- img-007: AI Generated Space Art
('img-007', (SELECT id FROM tags WHERE name = 'AI')),
('img-007', (SELECT id FROM tags WHERE name = 'artistic')),
('img-007', (SELECT id FROM tags WHERE name = 'abstract')),

-- img-008: Mountain Peak Sunrise
('img-008', (SELECT id FROM tags WHERE name = 'nature')),
('img-008', (SELECT id FROM tags WHERE name = 'landscape')),
('img-008', (SELECT id FROM tags WHERE name = 'mountains')),
('img-008', (SELECT id FROM tags WHERE name = 'sunset')),
('img-008', (SELECT id FROM tags WHERE name = 'photography'));
