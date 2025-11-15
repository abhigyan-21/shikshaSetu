"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import os

from .models import Base


class Database:
    """Manages PostgreSQL database connections with connection pooling."""
    
    def __init__(self):
        self.database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://user:password@localhost:5432/education_content'
        )
        
        # Create engine with connection pooling
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=os.getenv('SQL_ECHO', 'false').lower() == 'true'
        )
        
        # Create session factory
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.Session()
    
    def close_session(self):
        """Close the current session."""
        self.Session.remove()


# Global database instance (lazy initialization)
db = None

def get_db():
    """Get or create the global database instance."""
    global db
    if db is None:
        db = Database()
    return db
