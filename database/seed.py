#!/usr/bin/env python3
"""
Database Seeder for CloneGallery
Handles database seeding with sample data
"""

import sqlite3
import os
import glob
from pathlib import Path
from datetime import datetime

class DatabaseSeeder:
    def __init__(self, db_path='clonegallery.db'):
        self.db_path = db_path
        self.seeders_dir = Path(__file__).parent / 'seeders'
        
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_seeders_table(self):
        """Create seeders tracking table if it doesn't exist."""
        conn = self.get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS seeders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()
    
    def get_applied_seeders(self):
        """Get list of applied seeders."""
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT name FROM seeders ORDER BY name")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_seeder_files(self):
        """Get list of seeder files."""
        seeder_files = glob.glob(str(self.seeders_dir / "*.sql"))
        return sorted(seeder_files)
    
    def run_seeder(self, file_path):
        """Run a single seeder file."""
        filename = Path(file_path).name
        seeder_name = filename.replace('.sql', '')
        
        print(f"Running seeder {seeder_name}...")
        
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        conn = self.get_connection()
        try:
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    conn.execute(statement)
            
            # Record seeder as applied
            conn.execute("""
                INSERT OR IGNORE INTO seeders (name, description) 
                VALUES (?, ?)
            """, (seeder_name, f"Seeder applied from {filename}"))
            
            conn.commit()
            print(f"✅ Seeder {seeder_name} completed successfully")
            
        except Exception as e:
            print(f"❌ Seeder {seeder_name} failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def seed(self, force=False):
        """Run all seeders."""
        print("🌱 Starting database seeding...")
        
        # Create seeders table if it doesn't exist
        self.create_seeders_table()
        
        # Get seeder files
        seeder_files = self.get_seeder_files()
        
        if not seeder_files:
            print("❌ No seeder files found")
            return
        
        print(f"📋 Found {len(seeder_files)} seeder files")
        
        # Run each seeder
        for file_path in seeder_files:
            seeder_name = Path(file_path).name.replace('.sql', '')
            
            # Check if already applied (unless force)
            if not force and seeder_name in self.get_applied_seeders():
                print(f"⏭️  Seeder {seeder_name} already applied, skipping")
                continue
            
            try:
                self.run_seeder(file_path)
            except Exception as e:
                print(f"❌ Seeding failed at {seeder_name}. Stopping seeding process.")
                raise
        
        print("🎉 All seeders completed successfully!")
    
    def reset(self):
        """Reset all seeded data."""
        print("🔄 Resetting seeded data...")
        
        conn = self.get_connection()
        try:
            # Delete data in reverse order of dependencies
            tables = [
                'album_images', 'albums', 'image_tags', 'user_likes', 
                'ai_generation_meta', 'images', 'tags', 'users', 'analytics'
            ]
            
            for table in tables:
                conn.execute(f"DELETE FROM {table}")
                print(f"  🗑️  Cleared {table}")
            
            # Reset seeders tracking
            conn.execute("DELETE FROM seeders")
            
            conn.commit()
            print("✅ Database reset completed")
            
        except Exception as e:
            print(f"❌ Reset failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def status(self):
        """Show seeder status."""
        print("📊 Seeder Status:")
        print("=" * 50)
        
        applied = self.get_applied_seeders()
        seeder_files = self.get_seeder_files()
        
        print(f"Applied seeders: {len(applied)}")
        for name in applied:
            print(f"  ✅ {name}")
        
        print(f"\nAvailable seeders: {len(seeder_files)}")
        for file_path in seeder_files:
            name = Path(file_path).name.replace('.sql', '')
            status = "✅" if name in applied else "⏳"
            print(f"  {status} {name}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='CloneGallery Database Seeder')
    parser.add_argument('--db-path', default='clonegallery.db', help='Database file path')
    parser.add_argument('command', choices=['seed', 'reset', 'status'], help='Command to run')
    parser.add_argument('--force', action='store_true', help='Force re-run all seeders')
    
    args = parser.parse_args()
    
    seeder = DatabaseSeeder(args.db_path)
    
    if args.command == 'seed':
        seeder.seed(force=args.force)
    elif args.command == 'reset':
        seeder.reset()
    elif args.command == 'status':
        seeder.status()

if __name__ == "__main__":
    main()
