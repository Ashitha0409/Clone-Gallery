#!/usr/bin/env python3
"""
Initialize the SQLite database with the proper schema
"""

import sqlite3
import os

def init_database():
    """Initialize the SQLite database with the schema."""
    
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Connect to SQLite database
    db_path = 'clonegallery.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read and execute the schema
        with open('database/schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema (SQLite can handle multiple statements)
        cursor.executescript(schema_sql)
        
        conn.commit()
        print("✅ Database initialized successfully!")
        print(f"📁 Database file: {db_path}")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Created tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
