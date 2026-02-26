-- Initialize PostgreSQL database with pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE ai_copilot TO postgres;

-- Create schema if needed
-- Tables will be created by SQLAlchemy on app startup
