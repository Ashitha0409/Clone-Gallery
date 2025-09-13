#!/usr/bin/env python3
"""
Database Migration Manager for CloneGallery
Handles database migrations and schema updates
"""

import sqlite3
import os
import glob
from pathlib import Path
from datetime import datetime

class DatabaseMigrator:
    def __init__(self, db_path='clonegallery.db'):
        self.db_path = db_path
        self.migrations_dir = Path(__file__).parent / 'migrations'
        self.seeders_dir = Path(__file__).parent / 'seeders'
        
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_migrations_table(self):
        """Create migrations tracking table if it doesn't exist."""
        conn = self.get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    description TEXT,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()
    
    def get_applied_migrations(self):
        """Get list of applied migrations."""
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT version FROM migrations ORDER BY version")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_pending_migrations(self):
        """Get list of pending migrations."""
        applied = set(self.get_applied_migrations())
        migration_files = glob.glob(str(self.migrations_dir / "*.sql"))
        
        pending = []
        for file_path in migration_files:
            filename = Path(file_path).name
            version = filename.split('_')[0]
            if version not in applied:
                pending.append((version, file_path))
        
        return sorted(pending, key=lambda x: x[0])
    
    def run_migration(self, version, file_path):
        """Run a single migration file."""
        print(f"Running migration {version}...")
        
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        conn = self.get_connection()
        try:
            # Execute the entire SQL content as one statement
            # This handles triggers and other complex SQL structures
            conn.executescript(sql_content)
            conn.commit()
            print(f"✅ Migration {version} completed successfully")
            
        except Exception as e:
            print(f"❌ Migration {version} failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def migrate(self):
        """Run all pending migrations."""
        print("🔄 Starting database migration...")
        
        # Create migrations table if it doesn't exist
        self.create_migrations_table()
        
        # Get pending migrations
        pending = self.get_pending_migrations()
        
        if not pending:
            print("✅ Database is up to date, no migrations to run")
            return
        
        print(f"📋 Found {len(pending)} pending migrations")
        
        # Run each migration
        for version, file_path in pending:
            try:
                self.run_migration(version, file_path)
            except Exception as e:
                print(f"❌ Migration failed at {version}. Stopping migration process.")
                raise
        
        print("🎉 All migrations completed successfully!")
    
    def rollback(self, version):
        """Rollback to a specific migration version."""
        print(f"🔄 Rolling back to migration {version}...")
        # Note: SQLite doesn't support rollback easily, this would need custom implementation
        print("⚠️  Rollback not implemented for SQLite. Manual intervention required.")
    
    def status(self):
        """Show migration status."""
        print("📊 Migration Status:")
        print("=" * 50)
        
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        print(f"Applied migrations: {len(applied)}")
        for version in applied:
            print(f"  ✅ {version}")
        
        print(f"\nPending migrations: {len(pending)}")
        for version, file_path in pending:
            print(f"  ⏳ {version}")
        
        if not pending:
            print("🎉 Database is up to date!")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='CloneGallery Database Migrator')
    parser.add_argument('--db-path', default='clonegallery.db', help='Database file path')
    parser.add_argument('command', choices=['migrate', 'status', 'rollback'], help='Command to run')
    parser.add_argument('--version', help='Version for rollback')
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator(args.db_path)
    
    if args.command == 'migrate':
        migrator.migrate()
    elif args.command == 'status':
        migrator.status()
    elif args.command == 'rollback':
        if not args.version:
            print("❌ Version required for rollback")
            return
        migrator.rollback(args.version)

if __name__ == "__main__":
    main()
