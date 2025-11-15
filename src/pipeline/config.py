"""Configuration management for the content pipeline."""
import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class ModelConfig:
    """Model configuration for Hugging Face clients."""
    flant5_model_id: str
    indictrans2_model_id: str
    bert_model_id: str
    vits_model_id: str
    api_key: str


@dataclass
class APIConfig:
    """API server configuration."""
    flask_port: int = 5000
    fastapi_port: int = 8000
    flask_debug: bool = False
    secret_key: str = "dev-secret-key"


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    max_calls: int = 100
    time_window: int = 60


@dataclass
class StorageConfig:
    """Storage paths configuration."""
    audio_path: str
    cache_path: str


class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.database = DatabaseConfig(
            url=os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/education_content'),
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            echo=os.getenv('SQL_ECHO', 'false').lower() == 'true'
        )
        
        self.models = ModelConfig(
            flant5_model_id=os.getenv('FLANT5_MODEL_ID', 'google/flan-t5-base'),
            indictrans2_model_id=os.getenv('INDICTRANS2_MODEL_ID', 'ai4bharat/indictrans2-en-indic-1B'),
            bert_model_id=os.getenv('BERT_MODEL_ID', 'bert-base-multilingual-cased'),
            vits_model_id=os.getenv('VITS_MODEL_ID', 'facebook/mms-tts-hin'),
            api_key=os.getenv('HUGGINGFACE_API_KEY', '')
        )
        
        self.api = APIConfig(
            flask_port=int(os.getenv('FLASK_PORT', '5000')),
            fastapi_port=int(os.getenv('FASTAPI_PORT', '8000')),
            flask_debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
            secret_key=os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
        )
        
        self.rate_limit = RateLimitConfig(
            max_calls=int(os.getenv('RATE_LIMIT_CALLS', '100')),
            time_window=int(os.getenv('RATE_LIMIT_WINDOW', '60'))
        )
        
        self.storage = StorageConfig(
            audio_path=os.getenv('AUDIO_STORAGE_PATH', './data/audio'),
            cache_path=os.getenv('CONTENT_CACHE_PATH', './data/cache')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'database': self.database.__dict__,
            'models': self.models.__dict__,
            'api': self.api.__dict__,
            'rate_limit': self.rate_limit.__dict__,
            'storage': self.storage.__dict__
        }


# Global configuration instance
config = Config()
