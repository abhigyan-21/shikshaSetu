"""
Rate Limiting Configuration
Implements rate limiting for API endpoints to prevent abuse
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
import os

# Redis connection for distributed rate limiting
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_client = Redis.from_url(redis_url)

def get_limiter(app):
    """
    Configure and return Flask-Limiter instance
    
    Args:
        app: Flask application instance
        
    Returns:
        Configured Limiter instance
    """
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=redis_url,
        storage_options={"socket_connect_timeout": 30},
        strategy="fixed-window",
        default_limits=["200 per day", "50 per hour"],
        headers_enabled=True,
    )
    
    return limiter

# Rate limit configurations for different endpoints
RATE_LIMITS = {
    # Content processing - most resource intensive
    'process_content': [
        "5 per minute",
        "20 per hour",
        "100 per day"
    ],
    
    # Batch download - moderate resource usage
    'batch_download': [
        "10 per minute",
        "50 per hour",
        "200 per day"
    ],
    
    # Content retrieval - lighter operations
    'get_content': [
        "30 per minute",
        "200 per hour",
        "1000 per day"
    ],
    
    # Search operations
    'search': [
        "20 per minute",
        "100 per hour",
        "500 per day"
    ],
    
    # Health check - no limits
    'health': None,
    
    # Metrics - restricted access
    'metrics': [
        "60 per minute"
    ]
}

def apply_rate_limits(limiter, blueprint):
    """
    Apply rate limits to blueprint routes
    
    Args:
        limiter: Flask-Limiter instance
        blueprint: Flask blueprint to apply limits to
    """
    # Apply specific limits to routes
    for endpoint, limits in RATE_LIMITS.items():
        if limits:
            route_name = f"{blueprint.name}.{endpoint}"
            limiter.limit(limits)(blueprint.view_functions.get(endpoint))
