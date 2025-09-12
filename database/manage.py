#!/usr/bin/env python3
"""
Database Management Script for CloneGallery
Unified interface for migrations, seeding, and database operations
"""

import os
import sys
import argparse
from pathlib import Path

# Add the database directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from migrate import DatabaseMigrator
from seed import DatabaseSeeder

class DatabaseManager:
    def __init__(self, db_path='clonegallery.db'):
        self.db_path = db_path
        self.migrator = DatabaseMigrator(db_path)
        self.seeder = DatabaseSeeder(db_path)
    
    def setup(self):
        """Complete database setup (migrate + seed)."""
        print("🚀 Setting up CloneGallery database...")
        print("=" * 50)
        
        try:
            # Run migrations
            print("\n📋 Running migrations...")
            self.migrator.migrate()
            
            # Run seeders
            print("\n🌱 Seeding database...")
            self.seeder.seed()
            
            print("\n🎉 Database setup completed successfully!")
            self.status()
            
        except Exception as e:
            print(f"\n❌ Database setup failed: {e}")
            sys.exit(1)
    
    def migrate(self):
        """Run database migrations."""
        self.migrator.migrate()
    
    def seed(self, force=False):
        """Seed database with sample data."""
        self.seeder.seed(force=force)
    
    def reset(self):
        """Reset database (clear all data)."""
        print("⚠️  This will delete ALL data from the database!")
        response = input("Are you sure? Type 'yes' to continue: ")
        
        if response.lower() == 'yes':
            self.seeder.reset()
            print("✅ Database reset completed")
        else:
            print("❌ Reset cancelled")
    
    def status(self):
        """Show database status."""
        print("\n📊 Database Status:")
        print("=" * 50)
        
        # Check if database exists
        if not os.path.exists(self.db_path):
            print("❌ Database file not found")
            return
        
        # Show migration status
        print("\n🔄 Migration Status:")
        self.migrator.status()
        
        # Show seeder status
        print("\n🌱 Seeder Status:")
        self.seeder.status()
        
        # Show database info
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table counts
            tables = ['users', 'images', 'tags', 'albums', 'user_likes', 'analytics']
            print(f"\n📈 Data Summary:")
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  {table}: {count} records")
                except:
                    print(f"  {table}: table not found")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error reading database: {e}")
    
    def backup(self, backup_path=None):
        """Create database backup."""
        if not backup_path:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"clonegallery_backup_{timestamp}.db"
        
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
    
    def restore(self, backup_path):
        """Restore database from backup."""
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return
        
        import shutil
        try:
            shutil.copy2(backup_path, self.db_path)
            print(f"✅ Database restored from: {backup_path}")
        except Exception as e:
            print(f"❌ Restore failed: {e}")

def main():
    parser = argparse.ArgumentParser(description='CloneGallery Database Manager')
    parser.add_argument('--db-path', default='clonegallery.db', help='Database file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    subparsers.add_parser('setup', help='Complete database setup (migrate + seed)')
    
    # Migrate command
    subparsers.add_parser('migrate', help='Run database migrations')
    
    # Seed command
    seed_parser = subparsers.add_parser('seed', help='Seed database with sample data')
    seed_parser.add_argument('--force', action='store_true', help='Force re-run all seeders')
    
    # Reset command
    subparsers.add_parser('reset', help='Reset database (clear all data)')
    
    # Status command
    subparsers.add_parser('status', help='Show database status')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create database backup')
    backup_parser.add_argument('--output', help='Backup file path')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore database from backup')
    restore_parser.add_argument('backup_path', help='Backup file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = DatabaseManager(args.db_path)
    
    if args.command == 'setup':
        manager.setup()
    elif args.command == 'migrate':
        manager.migrate()
    elif args.command == 'seed':
        manager.seed(force=args.force)
    elif args.command == 'reset':
        manager.reset()
    elif args.command == 'status':
        manager.status()
    elif args.command == 'backup':
        manager.backup(args.output)
    elif args.command == 'restore':
        manager.restore(args.backup_path)

if __name__ == "__main__":
    main()
