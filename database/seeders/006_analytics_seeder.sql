-- Seeder: 006_analytics_seeder.sql
-- Description: Seed analytics table with sample metrics
-- Created: 2024-12-19

-- Insert sample analytics data
INSERT OR IGNORE INTO analytics (metric_name, metric_value, recorded_at) VALUES
('total_images', '1247', '2024-12-19T00:00:00Z'),
('total_users', '156', '2024-12-19T00:00:00Z'),
('total_views', '45680', '2024-12-19T00:00:00Z'),
('total_likes', '8934', '2024-12-19T00:00:00Z'),
('storage_used', '12.4 GB', '2024-12-19T00:00:00Z'),
('ai_generated', '234', '2024-12-19T00:00:00Z'),
('processing_queue', '3', '2024-12-19T00:00:00Z'),
('active_users_today', '23', '2024-12-19T00:00:00Z'),
('uploads_today', '12', '2024-12-19T00:00:00Z'),
('views_today', '456', '2024-12-19T00:00:00Z'),
('likes_today', '89', '2024-12-19T00:00:00Z'),
('avg_image_size', '2.3 MB', '2024-12-19T00:00:00Z'),
('most_popular_tag', 'nature', '2024-12-19T00:00:00Z'),
('ai_generation_success_rate', '94.2%', '2024-12-19T00:00:00Z'),
('avg_processing_time', '3.2s', '2024-12-19T00:00:00Z');
