-- Database initialization script for Education Content Pipeline
-- This script creates the necessary database schema

-- Create database if it doesn't exist (handled by docker-compose)
-- CREATE DATABASE IF NOT EXISTS education_content;

-- Connect to the database
\c education_content;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create processed_content table
CREATE TABLE IF NOT EXISTS processed_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_text TEXT NOT NULL,
    simplified_text TEXT,
    translated_text TEXT,
    language VARCHAR(50) NOT NULL,
    grade_level INTEGER NOT NULL CHECK (grade_level BETWEEN 5 AND 12),
    subject VARCHAR(100) NOT NULL,
    audio_file_path TEXT,
    ncert_alignment_score FLOAT CHECK (ncert_alignment_score BETWEEN 0 AND 1),
    audio_accuracy_score FLOAT CHECK (audio_accuracy_score BETWEEN 0 AND 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create ncert_standards table
CREATE TABLE IF NOT EXISTS ncert_standards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    grade_level INTEGER NOT NULL CHECK (grade_level BETWEEN 5 AND 12),
    subject VARCHAR(100) NOT NULL,
    topic VARCHAR(200) NOT NULL,
    learning_objectives TEXT[],
    keywords TEXT[]
);

-- Create student_profiles table
CREATE TABLE IF NOT EXISTS student_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    language_preference VARCHAR(50) NOT NULL,
    grade_level INTEGER NOT NULL CHECK (grade_level BETWEEN 5 AND 12),
    subjects_of_interest TEXT[],
    offline_content_cache JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create pipeline_logs table
CREATE TABLE IF NOT EXISTS pipeline_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES processed_content(id) ON DELETE CASCADE,
    stage VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    processing_time_ms INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_processed_content_language ON processed_content(language);
CREATE INDEX IF NOT EXISTS idx_processed_content_grade ON processed_content(grade_level);
CREATE INDEX IF NOT EXISTS idx_processed_content_subject ON processed_content(subject);
CREATE INDEX IF NOT EXISTS idx_processed_content_created ON processed_content(created_at);

CREATE INDEX IF NOT EXISTS idx_ncert_standards_grade ON ncert_standards(grade_level);
CREATE INDEX IF NOT EXISTS idx_ncert_standards_subject ON ncert_standards(subject);

CREATE INDEX IF NOT EXISTS idx_pipeline_logs_content ON pipeline_logs(content_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_logs_stage ON pipeline_logs(stage);
CREATE INDEX IF NOT EXISTS idx_pipeline_logs_timestamp ON pipeline_logs(timestamp);

-- Insert sample NCERT standards data
INSERT INTO ncert_standards (grade_level, subject, topic, learning_objectives, keywords)
VALUES 
    (8, 'Science', 'Photosynthesis', 
     ARRAY['Understand the process of photosynthesis', 'Identify chloroplasts role', 'Explain energy conversion'],
     ARRAY['photosynthesis', 'chlorophyll', 'sunlight', 'glucose', 'oxygen']),
    
    (8, 'Mathematics', 'Linear Equations',
     ARRAY['Solve linear equations', 'Understand variables', 'Apply algebraic methods'],
     ARRAY['equation', 'variable', 'algebra', 'coefficient', 'solution']),
    
    (10, 'Science', 'Chemical Reactions',
     ARRAY['Identify types of chemical reactions', 'Balance chemical equations', 'Understand reaction rates'],
     ARRAY['chemical reaction', 'reactants', 'products', 'catalyst', 'equilibrium']),
    
    (10, 'Mathematics', 'Quadratic Equations',
     ARRAY['Solve quadratic equations', 'Use quadratic formula', 'Understand roots'],
     ARRAY['quadratic', 'polynomial', 'discriminant', 'roots', 'parabola'])
ON CONFLICT DO NOTHING;

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Display success message
SELECT 'Database initialization completed successfully!' AS status;
