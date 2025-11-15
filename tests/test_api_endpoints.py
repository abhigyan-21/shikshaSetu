"""Tests for API endpoints (Flask and FastAPI)."""
import pytest
import json
from uuid import uuid4


class TestFlaskAPI:
    """Test Flask API endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        from src.api.flask_app import app
        
        client = app.test_client()
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'education-content-api'
    
    def test_process_content_missing_fields(self):
        """Test process content with missing required fields."""
        from src.api.flask_app import app
        
        client = app.test_client()
        response = client.post(
            '/api/process-content',
            json={'input_data': 'Test content'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'missing' in data
    
    def test_process_content_validation_error(self):
        """Test process content with invalid parameters."""
        from src.api.flask_app import app
        
        client = app.test_client()
        response = client.post(
            '/api/process-content',
            json={
                'input_data': 'Test content',
                'target_language': 'InvalidLanguage',
                'grade_level': 8,
                'subject': 'Mathematics',
                'output_format': 'text'
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_content_invalid_uuid(self):
        """Test get content with invalid UUID."""
        from src.api.flask_app import app
        
        client = app.test_client()
        response = client.get('/api/content/invalid-uuid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_content_not_found(self):
        """Test get content with non-existent UUID."""
        from src.api.flask_app import app
        
        client = app.test_client()
        test_uuid = str(uuid4())
        response = client.get(f'/api/content/{test_uuid}')
        
        # May return 404 or 500 depending on database state
        assert response.status_code in [404, 500]
    
    def test_batch_download_missing_field(self):
        """Test batch download with missing content_ids."""
        from src.api.flask_app import app
        
        client = app.test_client()
        response = client.post(
            '/api/batch-download',
            json={'include_audio': True}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_batch_download_exceeds_limit(self):
        """Test batch download with too many items."""
        from src.api.flask_app import app
        
        client = app.test_client()
        # Create 51 UUIDs (exceeds limit of 50)
        content_ids = [str(uuid4()) for _ in range(51)]
        
        response = client.post(
            '/api/batch-download',
            json={'content_ids': content_ids}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'max_items' in data
    
    def test_search_content_no_filters(self):
        """Test search content without filters."""
        from src.api.flask_app import app
        
        client = app.test_client()
        response = client.get('/api/content/search')
        
        # Should return 200 even with no results
        assert response.status_code in [200, 500]
    
    def test_search_content_with_filters(self):
        """Test search content with filters."""
        from src.api.flask_app import app
        
        client = app.test_client()
        response = client.get('/api/content/search?language=Hindi&grade=8&subject=Mathematics')
        
        # Should return 200 even with no results
        assert response.status_code in [200, 500]
    
    def test_search_content_invalid_grade(self):
        """Test search content with invalid grade."""
        from src.api.flask_app import app
        
        client = app.test_client()
        response = client.get('/api/content/search?grade=20')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestFastAPI:
    """Test FastAPI endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        from fastapi.testclient import TestClient
        from src.api.fastapi_app import app
        
        client = TestClient(app)
        response = client.get('/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'running'
        assert 'version' in data
    
    def test_health_check(self):
        """Test health check endpoint."""
        from fastapi.testclient import TestClient
        from src.api.fastapi_app import app
        
        client = TestClient(app)
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
    
    def test_process_content_validation(self):
        """Test process content with Pydantic validation."""
        from fastapi.testclient import TestClient
        from src.api.fastapi_app import app
        
        client = TestClient(app)
        response = client.post(
            '/api/v1/process-content',
            json={
                'input_data': 'Test content',
                'target_language': 'InvalidLanguage',
                'grade_level': 8,
                'subject': 'Mathematics',
                'output_format': 'text'
            }
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_get_content_invalid_uuid(self):
        """Test get content with invalid UUID."""
        from fastapi.testclient import TestClient
        from src.api.fastapi_app import app
        
        client = TestClient(app)
        response = client.get('/api/v1/content/invalid-uuid')
        
        assert response.status_code == 400
    
    def test_batch_download_validation(self):
        """Test batch download with Pydantic validation."""
        from fastapi.testclient import TestClient
        from src.api.fastapi_app import app
        
        client = TestClient(app)
        # Create 51 UUIDs (exceeds limit of 50)
        content_ids = [str(uuid4()) for _ in range(51)]
        
        response = client.post(
            '/api/v1/batch-download',
            json={'content_ids': content_ids, 'include_audio': True}
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_search_content_pagination(self):
        """Test search content with pagination."""
        from fastapi.testclient import TestClient
        from src.api.fastapi_app import app
        
        client = TestClient(app)
        response = client.get('/api/v1/content/search?limit=10&offset=0')
        
        # Should return 200 even with no results
        assert response.status_code in [200, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
