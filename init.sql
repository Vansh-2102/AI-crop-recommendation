-- Database initialization script for Crop Recommendation Platform
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE crop_recommendation_prod'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'crop_recommendation_prod')\gexec

-- Connect to the database
\c crop_recommendation_prod;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- (Tables will be created by SQLAlchemy, but we can add indexes here)

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE crop_recommendation_prod TO postgres;

-- Create a read-only user for monitoring
CREATE USER monitor_user WITH PASSWORD 'monitor_password';
GRANT CONNECT ON DATABASE crop_recommendation_prod TO monitor_user;
GRANT USAGE ON SCHEMA public TO monitor_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitor_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO monitor_user;

