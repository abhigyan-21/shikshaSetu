"""SQLAlchemy ORM models for the content repository."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class ProcessedContent(Base):
    """Stores processed educational content with translations and audio."""
    __tablename__ = 'processed_content'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_text = Column(Text, nullable=False)
    simplified_text = Column(Text)
    translated_text = Column(Text)
    language = Column(String(50), nullable=False)
    grade_level = Column(Integer, nullable=False)
    subject = Column(String(100), nullable=False)
    audio_file_path = Column(Text)
    ncert_alignment_score = Column(Float)
    audio_accuracy_score = Column(Float)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    content_metadata = Column('metadata', JSONB)


class NCERTStandard(Base):
    """Reference database for NCERT curriculum standards."""
    __tablename__ = 'ncert_standards'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grade_level = Column(Integer, nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=False)
    learning_objectives = Column(ARRAY(Text))
    keywords = Column(ARRAY(Text))


class StudentProfile(Base):
    """User profiles with language preferences and learning data."""
    __tablename__ = 'student_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    language_preference = Column(String(50), nullable=False)
    grade_level = Column(Integer, nullable=False)
    subjects_of_interest = Column(ARRAY(Text))
    offline_content_cache = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class PipelineLog(Base):
    """Logs for pipeline processing stages and performance metrics."""
    __tablename__ = 'pipeline_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('processed_content.id'))
    stage = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    processing_time_ms = Column(Integer)
    error_message = Column(Text)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
