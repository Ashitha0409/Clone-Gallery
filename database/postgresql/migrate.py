#!/usr/bin/env python3
"""
PostgreSQL Migration Manager for CloneGallery
Handles database migrations and schema updates for production
"""

import psycopg2
import psycopg2.extras
import os
import glob
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLMigrator:
    def __init__(self, db_config=None):
        self.db_config = db_config or {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'clonegallery'),
            'user': os.getenv('POSTGRES_USER', 'clonegallery'),
            'password': os.getenv('POSTGRES_PASSWORD', 'clonegallery')
        }
        self.migrations_dir = Path(__file__).parent / 'migrations'
        
    def get_connection(self):
        """Get database connection."""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = False
            return conn
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def create_migrations_table(self):
        """Create migrations tracking table if it doesn't exist."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS migrations (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(20) UNIQUE NOT NULL,
                        description TEXT,
                        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                conn.commit()
        except psycopg2.Error as e:
            logger.error(f"Failed to create migrations table: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_applied_migrations(self):
        """Get list of applied migrations."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version FROM migrations ORDER BY version")
                return [row[0] for row in cursor.fetchall()]
        except psycopg2.Error as e:
            logger.error(f"Failed to get applied migrations: {e}")
            raise
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
        logger.info(f"Running migration {version}...")
        
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
                for statement in statements:
                    if statement:
                        cursor.execute(statement)
                
                # Record migration as applied
                cursor.execute("""
                    INSERT INTO migrations (version, description) 
                    VALUES (%s, %s)
                """, (version, f"Migration applied from {Path(file_path).name}"))
                
                conn.commit()
                logger.info(f"✅ Migration {version} completed successfully")
                
        except psycopg2.Error as e:
            logger.error(f"❌ Migration {version} failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def migrate(self):
        """Run all pending migrations."""
        logger.info("🔄 Starting PostgreSQL migration...")
        
        # Create migrations table if it doesn't exist
        self.create_migrations_table()
        
        # Get pending migrations
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("✅ Database is up to date, no migrations to run")
            return
        
        logger.info(f"📋 Found {len(pending)} pending migrations")
        
        # Run each migration
        for version, file_path in pending:
            try:
                self.run_migration(version, file_path)
            except Exception as e:
                logger.error(f"❌ Migration failed at {version}. Stopping migration process.")
                raise
        
        logger.info("🎉 All migrations completed successfully!")
    
    def rollback(self, version):
        """Rollback to a specific migration version."""
        logger.warning(f"🔄 Rolling back to migration {version}...")
        logger.warning("⚠️  Rollback not implemented for PostgreSQL. Manual intervention required.")
    
    def status(self):
        """Show migration status."""
        logger.info("📊 Migration Status:")
        logger.info("=" * 50)
        
        try:
            applied = self.get_applied_migrations()
            pending = self.get_pending_migrations()
            
            logger.info(f"Applied migrations: {len(applied)}")
            for version in applied:
                logger.info(f"  ✅ {version}")
            
            logger.info(f"\nPending migrations: {len(pending)}")
            for version, file_path in pending:
                logger.info(f"  ⏳ {version}")
            
            if not pending:
                logger.info("🎉 Database is up to date!")
                
        except Exception as e:
            logger.error(f"❌ Failed to get migration status: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='CloneGallery PostgreSQL Migrator')
    parser.add_argument('--host', default=os.getenv('POSTGRES_HOST', 'localhost'), help='Database host')
    parser.add_argument('--port', default=os.getenv('POSTGRES_PORT', '5432'), help='Database port')
    parser.add_argument('--database', default=os.getenv('POSTGRES_DB', 'clonegallery'), help='Database name')
    parser.add_argument('--user', default=os.getenv('POSTGRES_USER', 'clonegallery'), help='Database user')
    parser.add_argument('--password', default=os.getenv('POSTGRES_PASSWORD', 'clonegallery'), help='Database password')
    parser.add_argument('command', choices=['migrate', 'status', 'rollback'], help='Command to run')
    parser.add_argument('--version', help='Version for rollback')
    
    args = parser.parse_args()
    
    db_config = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user,
        'password': args.password
    }
    
    migrator = PostgreSQLMigrator(db_config)
    
    if args.command == 'migrate':
        migrator.migrate()
    elif args.command == 'status':
        migrator.status()
    elif args.command == 'rollback':
        if not args.version:
            logger.error("❌ Version required for rollback")
            return
        migrator.rollback(args.version)

if __name__ == "__main__":
    main()
