-- Seeder: 001_users_seeder.sql
-- Description: Seed users table with demo accounts
-- Created: 2024-12-19

-- Insert demo users
INSERT OR IGNORE INTO users (id, email, name, role, avatar, joined_at, uploads, views) VALUES
('admin-001', 'admin@clonegallery.local', 'Gallery Admin', 'Admin', 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face', '2024-01-15T00:00:00Z', 45, 12500),
('editor-001', 'editor@clonegallery.local', 'Creative Editor', 'Editor', 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face', '2024-02-20T00:00:00Z', 28, 8200),
('visitor-001', 'user@clonegallery.local', 'Gallery Visitor', 'Visitor', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face', '2024-03-10T00:00:00Z', 0, 350),
('admin-002', 'demo@clonegallery.local', 'Demo Admin', 'Admin', 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=100&h=100&fit=crop&crop=face', '2024-04-01T00:00:00Z', 12, 2100),
('editor-002', 'photographer@clonegallery.local', 'Professional Photographer', 'Editor', 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=face', '2024-04-15T00:00:00Z', 67, 15600);
