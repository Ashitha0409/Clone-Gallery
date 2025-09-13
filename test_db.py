#!/usr/bin/env python3
"""
Test database connection and operations
"""

import sqlite3
import uuid
from datetime import datetime, timezone
from passlib.context import CryptContext

def test_database():
    """Test database operations."""
    
    try:
        print("🧪 Testing database connection...")
        
        # Connect to database
        conn = sqlite3.connect('clonegallery.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("✅ Database connected successfully!")
        
        # Test user creation
        print("🧪 Testing user creation...")
        
        user_id = str(uuid.uuid4())
        email = "test@example.com"
        username = "testuser"
        name = "Test User"
        role = "Visitor"
        
        # Hash password
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash("testpassword123")
        
        # Insert user
        query = """
            INSERT INTO users (id, email, username, password_hash, name, role, joined_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            user_id, email, username, password_hash,
            name, role, datetime.now(timezone.utc)
        )
        
        cursor.execute(query, params)
        conn.commit()
        
        print("✅ User created successfully!")
        
        # Test user retrieval
        print("🧪 Testing user retrieval...")
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            print("✅ User retrieved successfully!")
            print(f"📄 User data: {dict(user)}")
        else:
            print("❌ User not found!")
        
        # Clean up
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        print("🧹 Test user cleaned up")
        
        conn.close()
        print("✅ Database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        print(f"📄 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_database()

