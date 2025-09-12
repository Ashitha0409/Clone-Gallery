-- PostgreSQL Initialization Script for CloneGallery
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist (handled by POSTGRES_DB)
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Note: The actual schema will be created by migrations
-- This file is for any pre-migration setup if needed

-- Create a simple function to check if migrations table exists
CREATE OR REPLACE FUNCTION check_migrations_table()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'migrations'
    );
END;
$$ LANGUAGE plpgsql;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL database initialized for CloneGallery';
    RAISE NOTICE 'Database: %', current_database();
    RAISE NOTICE 'User: %', current_user;
    RAISE NOTICE 'Extensions available: uuid-ossp, pg_trgm, btree_gin';
END $$;
