#!/usr/bin/env python3
"""
Integration Verification Script

This script verifies that all components are properly integrated:
1. Pipeline orchestrator connects to all components
2. API endpoints connect to orchestrator
3. Repository stores and retrieves content
4. Frontend can communicate with backend
5. Complete end-to-end flow works

Run this script to verify the integration is complete.
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.integration import test_end_to_end_flow, get_integrated_pipeline


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_success(text):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text):
    """Print error message."""
    print(f"✗ {text}")


def print_info(text):
    """Print info message."""
    print(f"  {text}")


def verify_component_imports():
    """Verify all components can be imported."""
    print_header("STEP 1: Verifying Component Imports")
    
    try:
        from src.pipeline.orchestrator import ContentPipelineOrchestrator
        print_success("Pipeline Orchestrator imported")
        
        from src.repository.content_repository import ContentRepository
        print_success("Content Repository imported")
        
        from src.repository.database import init_db, get_db
        print_success("Database module imported")
        
        from src.monitoring.metrics_collector import MetricsCollector
        print_success("Metrics Collector imported")
        
        from src.api.flask_app import app as flask_app
        print_success("Flask API imported")
        
        from src.api.fastapi_app import app as fastapi_app
        print_success("FastAPI imported")
        
        return True
        
    except Exception as e:
        print_error(f"Import failed: {str(e)}")
        return False


def verify_database_connection():
    """Verify database connection."""
    print_header("STEP 2: Verifying Database Connection")
    
    try:
        from src.repository.database import init_db, get_db
        
        # Initialize database
        init_db()
        print_success("Database initialized")
        
        # Test connection
        session = get_db().get_session()
        session.execute("SELECT 1")
        session.close()
        print_success("Database connection verified")
        
        return True
        
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        return False


def verify_integrated_pipeline():
    """Verify integrated pipeline initialization."""
    print_header("STEP 3: Verifying Integrated Pipeline")
    
    try:
        pipeline = get_integrated_pipeline()
        print_success("Integrated pipeline created")
        
        # Check components
        assert hasattr(pipeline, 'orchestrator'), "Missing orchestrator"
        print_success("Orchestrator connected")
        
        assert hasattr(pipeline, 'repository'), "Missing repository"
        print_success("Repository connected")
        
        assert hasattr(pipeline, 'metrics_collector'), "Missing metrics collector"
        print_success("Metrics collector connected")
        
        return True
        
    except Exception as e:
        print_error(f"Pipeline verification failed: {str(e)}")
        return False


def verify_end_to_end_flow():
    """Verify complete end-to-end flow."""
    print_header("STEP 4: Verifying End-to-End Flow")
    
    try:
        print_info("Running end-to-end test with sample content...")
        
        result = test_end_to_end_flow(
            sample_text="The water cycle is the continuous movement of water on, above, and below the surface of the Earth.",
            target_language='Hindi',
            grade_level=7,
            subject='Science'
        )
        
        if not result['success']:
            print_error(f"End-to-end test failed: {result.get('error')}")
            return False
        
        print_success("Content processing completed")
        print_info(f"  Content ID: {result['content_id']}")
        print_info(f"  NCERT Score: {result['processing_result']['quality_scores']['ncert_alignment_score']:.2%}")
        print_info(f"  Processing Time: {result['processing_result']['metrics']['total_processing_time_ms']}ms")
        
        print_success("Content retrieval verified")
        print_success("Search functionality verified")
        print_success("Offline package creation verified")
        print_success("System health check verified")
        
        return True
        
    except Exception as e:
        print_error(f"End-to-end flow failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_api_endpoints():
    """Verify API endpoints are properly configured."""
    print_header("STEP 5: Verifying API Endpoints")
    
    try:
        from src.api.flask_app import app as flask_app
        
        # Check Flask routes
        routes = [rule.rule for rule in flask_app.url_map.iter_rules()]
        
        required_routes = [
            '/api/process-content',
            '/api/content/<content_id>',
            '/api/batch-download',
            '/api/content/search'
        ]
        
        for route in required_routes:
            # Check if route pattern exists
            route_exists = any(route.replace('<content_id>', '<') in r for r in routes)
            if route_exists:
                print_success(f"Flask route configured: {route}")
            else:
                print_error(f"Flask route missing: {route}")
                return False
        
        print_success("All Flask API endpoints configured")
        
        # Check FastAPI
        from src.api.fastapi_app import app as fastapi_app
        
        fastapi_routes = [route.path for route in fastapi_app.routes]
        
        required_fastapi_routes = [
            '/api/v1/process-content',
            '/api/v1/content/{content_id}',
            '/api/v1/batch-download',
            '/api/v1/content/search'
        ]
        
        for route in required_fastapi_routes:
            route_exists = any(route in r for r in fastapi_routes)
            if route_exists:
                print_success(f"FastAPI route configured: {route}")
            else:
                print_error(f"FastAPI route missing: {route}")
                return False
        
        print_success("All FastAPI endpoints configured")
        
        return True
        
    except Exception as e:
        print_error(f"API endpoint verification failed: {str(e)}")
        return False


def verify_frontend_integration():
    """Verify frontend files exist and are configured."""
    print_header("STEP 6: Verifying Frontend Integration")
    
    try:
        # Check frontend files exist
        frontend_files = [
            'frontend/src/App.jsx',
            'frontend/src/pages/UploadPage.jsx',
            'frontend/src/pages/ContentViewerPage.jsx',
            'frontend/src/pages/OfflineContentPage.jsx',
            'frontend/src/utils/api.js'
        ]
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                print_success(f"Frontend file exists: {file_path}")
            else:
                print_error(f"Frontend file missing: {file_path}")
                return False
        
        # Check API utility has required functions
        with open('frontend/src/utils/api.js', 'r') as f:
            api_content = f.read()
            
        required_functions = [
            'processContent',
            'getContent',
            'searchContent',
            'createBatchDownload'
        ]
        
        for func in required_functions:
            if func in api_content:
                print_success(f"API function defined: {func}")
            else:
                print_error(f"API function missing: {func}")
                return False
        
        print_success("Frontend integration verified")
        
        return True
        
    except Exception as e:
        print_error(f"Frontend verification failed: {str(e)}")
        return False


def main():
    """Run all verification steps."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "INTEGRATION VERIFICATION SCRIPT" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")
    
    start_time = datetime.now()
    
    # Run verification steps
    steps = [
        ("Component Imports", verify_component_imports),
        ("Database Connection", verify_database_connection),
        ("Integrated Pipeline", verify_integrated_pipeline),
        ("End-to-End Flow", verify_end_to_end_flow),
        ("API Endpoints", verify_api_endpoints),
        ("Frontend Integration", verify_frontend_integration)
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            success = step_func()
            results.append((step_name, success))
        except Exception as e:
            print_error(f"Step '{step_name}' crashed: {str(e)}")
            results.append((step_name, False))
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for step_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {step_name:.<50} {status}")
    
    print("\n" + "-" * 80)
    print(f"  Total: {passed}/{total} steps passed")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"  Duration: {duration:.2f} seconds")
    print("-" * 80 + "\n")
    
    if passed == total:
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "✓ ALL CHECKS PASSED!" + " " * 32 + "║")
        print("║" + " " * 15 + "Integration is complete and working correctly." + " " * 17 + "║")
        print("╚" + "=" * 78 + "╝\n")
        return 0
    else:
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "✗ SOME CHECKS FAILED" + " " * 33 + "║")
        print("║" + " " * 12 + "Please review the errors above and fix the issues." + " " * 15 + "║")
        print("╚" + "=" * 78 + "╝\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
