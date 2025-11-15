"""
Example usage of ContentPipelineOrchestrator.

This script demonstrates how to use the orchestrator to process educational content
through the complete pipeline (simplification, translation, validation, speech generation).

Note: This example requires:
1. PostgreSQL database running
2. Hugging Face API key set in environment
3. All dependencies installed
"""
import os
import sys

# Add parent directory to path to import src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline.orchestrator import ContentPipelineOrchestrator, PipelineValidationError


def main():
    """Demonstrate orchestrator usage."""
    
    # Initialize the orchestrator
    print("Initializing Content Pipeline Orchestrator...")
    orchestrator = ContentPipelineOrchestrator()
    
    # Example 1: Valid parameter validation
    print("\n=== Example 1: Parameter Validation ===")
    try:
        orchestrator.validate_parameters(
            input_data="Photosynthesis is the process by which plants convert light energy into chemical energy.",
            target_language="Hindi",
            grade_level=8,
            subject="Science",
            output_format="both"
        )
        print("✓ Parameters validated successfully")
    except PipelineValidationError as e:
        print(f"✗ Validation failed: {e}")
    
    # Example 2: Invalid parameters
    print("\n=== Example 2: Invalid Parameters ===")
    try:
        orchestrator.validate_parameters(
            input_data="",
            target_language="French",
            grade_level=15,
            subject="Art",
            output_format="video"
        )
        print("✓ Parameters validated successfully")
    except PipelineValidationError as e:
        print(f"✗ Validation failed (expected):\n{e}")
    
    # Example 3: Test all supported languages
    print("\n=== Example 3: Supported Languages ===")
    print(f"Supported languages: {', '.join(orchestrator.SUPPORTED_LANGUAGES)}")
    
    # Example 4: Test all supported subjects
    print("\n=== Example 4: Supported Subjects ===")
    print(f"Supported subjects: {', '.join(orchestrator.SUPPORTED_SUBJECTS)}")
    
    # Example 5: Test all supported formats
    print("\n=== Example 5: Supported Output Formats ===")
    print(f"Supported formats: {', '.join(orchestrator.SUPPORTED_FORMATS)}")
    
    # Example 6: Grade level range
    print("\n=== Example 6: Grade Level Range ===")
    print(f"Supported grade levels: {orchestrator.MIN_GRADE} to {orchestrator.MAX_GRADE}")
    
    # Example 7: Metrics tracking
    print("\n=== Example 7: Metrics Tracking ===")
    orchestrator.track_metrics("simplification", 1500, True)
    orchestrator.track_metrics("translation", 2000, True)
    orchestrator.track_metrics("validation", 1000, True)
    orchestrator.track_metrics("speech", 3000, True)
    
    print(f"Tracked {len(orchestrator.metrics)} pipeline stages:")
    for metric in orchestrator.metrics:
        status = "✓" if metric.success else "✗"
        print(f"  {status} {metric.stage}: {metric.processing_time_ms}ms")
    
    total_time = sum(m.processing_time_ms for m in orchestrator.metrics)
    print(f"Total processing time: {total_time}ms")
    
    # Example 8: Full pipeline processing (commented out - requires API keys and database)
    print("\n=== Example 8: Full Pipeline Processing ===")
    print("Note: Uncomment the code below to run full pipeline processing")
    print("Requirements: PostgreSQL database, Hugging Face API key")
    
    """
    # Uncomment to run full pipeline processing:
    
    try:
        result = orchestrator.process_content(
            input_data="The water cycle describes how water evaporates from the surface of the earth, rises into the atmosphere, cools and condenses into rain or snow in clouds, and falls again to the surface as precipitation.",
            target_language="Hindi",
            grade_level=8,
            subject="Science",
            output_format="both"
        )
        
        print(f"✓ Content processed successfully!")
        print(f"  Content ID: {result.id}")
        print(f"  Language: {result.language}")
        print(f"  Grade Level: {result.grade_level}")
        print(f"  NCERT Alignment Score: {result.ncert_alignment_score:.2f}")
        print(f"  Validation Status: {result.validation_status}")
        
        if result.audio_file_path:
            print(f"  Audio File: {result.audio_file_path}")
            print(f"  Audio Accuracy: {result.audio_accuracy_score:.2f}")
        
        print(f"\nPipeline Metrics:")
        for metric in result.metrics:
            status = "✓" if metric.success else "✗"
            print(f"  {status} {metric.stage}: {metric.processing_time_ms}ms")
        
    except PipelineValidationError as e:
        print(f"✗ Validation error: {e}")
    except Exception as e:
        print(f"✗ Processing error: {e}")
    """
    
    print("\n=== Orchestrator Example Complete ===")


if __name__ == "__main__":
    main()
