#!/usr/bin/env python3
"""
Database initialization script for CloneGallery
Creates tables and populates with sample data
"""

import sqlite3
import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Database configuration
DB_PATH = os.getenv('DATABASE_PATH', 'clonegallery.db')
SCHEMA_PATH = Path(__file__).parent / 'schema.sql'

def init_database():
    """Initialize the database with schema and sample data."""
    print(f"Initializing database at {DB_PATH}")
    
    # Create database connection
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    try:
        # Read and execute schema
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
        
        cursor.executescript(schema_sql)
        print("✓ Database schema created")
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("✓ Populating with sample data...")
            populate_sample_data(cursor)
        else:
            print("✓ Database already contains data, skipping sample data")
        
        conn.commit()
        print("✓ Database initialization complete")
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def populate_sample_data(cursor):
    """Populate database with sample data."""
    
    # Sample users
    users = [
        {
            'id': 'admin-001',
            'email': 'admin@clonegallery.local',
            'username': 'admin',
            'name': 'Gallery Admin',
            'role': 'Admin',
            'password': 'admin123',
            'avatar': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
            'joined': '2024-01-15T00:00:00Z',
            'uploads': 45,
            'views': 12500
        },
        {
            'id': 'editor-001',
            'email': 'editor@clonegallery.local',
            'username': 'editor',
            'name': 'Creative Editor',
            'role': 'Editor',
            'password': 'editor123',
            'avatar': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
            'joined': '2024-02-20T00:00:00Z',
            'uploads': 28,
            'views': 8200
        },
        {
            'id': 'visitor-001',
            'email': 'user@clonegallery.local',
            'username': 'visitor',
            'name': 'Gallery Visitor',
            'role': 'Visitor',
            'password': 'user123',
            'avatar': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
            'joined': '2024-03-10T00:00:00Z',
            'uploads': 0,
            'views': 350
        }
    ]
    
    # Import password hashing library
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Insert users
    for user in users:
        # Hash the password
        password_hash = pwd_context.hash(user['password'])
        
        cursor.execute("""
            INSERT INTO users (id, email, username, password_hash, name, role, avatar, joined_at, uploads, views)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user['id'], user['email'], user['username'], password_hash, user['name'], user['role'],
            user['avatar'], user['joined'], user['uploads'], user['views']
        ))
    
    # Sample tags
    tags = [
        {'name': 'nature', 'count': 124, 'trending': True},
        {'name': 'landscape', 'count': 89, 'trending': True},
        {'name': 'architecture', 'count': 67, 'trending': False},
        {'name': 'AI', 'count': 45, 'trending': True},
        {'name': 'urban', 'count': 56, 'trending': False},
        {'name': 'abstract', 'count': 34, 'trending': False},
        {'name': 'mountains', 'count': 78, 'trending': True},
        {'name': 'ocean', 'count': 92, 'trending': False}
    ]
    
    # Insert tags
    for tag in tags:
        cursor.execute("""
            INSERT INTO tags (name, count, trending)
            VALUES (?, ?, ?)
        """, (tag['name'], tag['count'], tag['trending']))
    
    # Sample images
    images = [
        {
            'id': 'img-001',
            'title': 'Mountain Lake Sunset',
            'caption': 'Beautiful alpine lake reflecting golden sunset colors with snow-capped mountains in the background',
            'alt_text': 'Alpine lake at sunset with mountain reflection',
            'url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
            'thumbnail': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=200&fit=crop',
            'uploader_id': 'admin-001',
            'uploaded_at': '2024-09-10T14:30:00Z',
            'tags': ['nature', 'landscape', 'sunset', 'mountains', 'lake'],
            'privacy': 'public',
            'likes': 24,
            'views': 156,
            'is_ai_generated': False,
            'width': 1920,
            'height': 1280,
            'size': '2.4 MB',
            'format': 'JPEG'
        },
        {
            'id': 'img-002',
            'title': 'Urban Architecture Dreams',
            'caption': 'Modern glass skyscraper with geometric patterns and reflective surfaces creating abstract art',
            'alt_text': 'Modern glass building with geometric reflections',
            'url': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=600&fit=crop',
            'thumbnail': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=300&h=200&fit=crop',
            'uploader_id': 'editor-001',
            'uploaded_at': '2024-09-09T16:45:00Z',
            'tags': ['architecture', 'urban', 'modern', 'glass', 'reflection'],
            'privacy': 'public',
            'likes': 31,
            'views': 203,
            'is_ai_generated': False,
            'width': 1920,
            'height': 1280,
            'size': '3.1 MB',
            'format': 'JPEG'
        },
        {
            'id': 'img-003',
            'title': 'AI Generated Forest',
            'caption': 'Mystical forest scene generated with Stable Diffusion featuring ethereal lighting and fantasy elements',
            'alt_text': 'AI-generated mystical forest with magical lighting',
            'url': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop',
            'thumbnail': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=300&h=200&fit=crop',
            'uploader_id': 'admin-001',
            'uploaded_at': '2024-09-08T10:20:00Z',
            'tags': ['AI', 'forest', 'mystical', 'fantasy', 'generated'],
            'privacy': 'public',
            'likes': 67,
            'views': 342,
            'is_ai_generated': True,
            'width': 1024,
            'height': 1024,
            'size': '1.8 MB',
            'format': 'PNG'
        }
    ]
    
    # Insert images
    for image in images:
        cursor.execute("""
            INSERT INTO images (id, title, caption, alt_text, url, thumbnail, uploader_id, 
                              uploaded_at, privacy, views, is_ai_generated, width, height, size, format)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            image['id'], image['title'], image['caption'], image['alt_text'],
            image['url'], image['thumbnail'], image['uploader_id'], image['uploaded_at'],
            image['privacy'], image['views'], image['is_ai_generated'],
            image['width'], image['height'], image['size'], image['format']
        ))
        
        # Insert image tags
        for tag_name in image['tags']:
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_result = cursor.fetchone()
            if tag_result:
                cursor.execute("""
                    INSERT INTO image_tags (image_id, tag_id)
                    VALUES (?, ?)
                """, (image['id'], tag_result[0]))
    
    # Sample albums
    albums = [
        {
            'id': 'album-001',
            'title': 'Nature Collection',
            'description': 'Curated collection of stunning nature photography from around the world',
            'cover_image_id': 'img-001',
            'created_by': 'admin-001',
            'created_at': '2024-09-01T10:00:00Z',
            'privacy': 'public',
            'images': ['img-001']
        }
    ]
    
    # Insert albums
    for album in albums:
        cursor.execute("""
            INSERT INTO albums (id, title, description, cover_image_id, created_by, created_at, privacy)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            album['id'], album['title'], album['description'], album['cover_image_id'],
            album['created_by'], album['created_at'], album['privacy']
        ))
        
        # Insert album images
        for i, image_id in enumerate(album['images']):
            cursor.execute("""
                INSERT INTO album_images (album_id, image_id, position)
                VALUES (?, ?, ?)
            """, (album['id'], image_id, i))
    
    # Sample analytics
    analytics = [
        ('total_images', '1247'),
        ('total_users', '156'),
        ('total_views', '45680'),
        ('total_likes', '8934'),
        ('storage_used', '12.4 GB'),
        ('ai_generated', '234'),
        ('processing_queue', '3')
    ]
    
    # Insert analytics
    for metric_name, metric_value in analytics:
        cursor.execute("""
            INSERT INTO analytics (metric_name, metric_value)
            VALUES (?, ?)
        """, (metric_name, metric_value))

def get_database_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    init_database()
