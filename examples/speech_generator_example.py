"""Example usage of the Speech Generator component."""
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.speech import SpeechGenerator, AudioFile


def main():
    """Demonstrate Speech Generator functionality."""
    print("Speech Generator Example")
    print("=" * 50)
    
    # Initialize the Speech Generator
    speech_generator = SpeechGenerator()
    
    # Display supported languages
    print(f"Supported languages: {', '.join(speech_generator.get_supported_languages())}")
    print()
    
    # Example content for different subjects
    examples = [
        {
            'text': "Photosynthesis is the process by which plants convert sunlight into energy. This happens in the chloroplasts of plant cells.",
            'language': 'Hindi',
            'subject': 'Science'
        },
        {
            'text': "To solve this equation, we need to isolate the variable x. First, add 5 to both sides of the equation.",
            'language': 'Tamil',
            'subject': 'Mathematics'
        },
        {
            'text': "The water cycle describes how water moves through the environment. It includes evaporation, condensation, and precipitation.",
            'language': 'Bengali',
            'subject': 'Science'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"Example {i}: {example['subject']} content in {example['language']}")
        print(f"Text: {example['text'][:60]}...")
        
        try:
            # Estimate audio size before generation
            estimated_size = speech_generator.estimate_audio_size(
                example['text'], 
                example['language']
            )
            print(f"Estimated audio size: {estimated_size:.2f} MB")
            
            # Note: In a real scenario, this would generate actual audio
            # For this example, we'll simulate the process
            print("⚠️  Note: This example uses mock TTS services for demonstration")
            print("   In production, it would connect to VITS or Bhashini TTS APIs")
            
            # Simulate audio generation (would normally call generate_speech)
            print("✓ Speech generation would complete here")
            print("✓ Audio optimization would be applied")
            print("✓ ASR validation would verify accuracy")
            print("✓ Audio file would be saved to storage")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    # Demonstrate technical term handling
    print("\nTechnical Term Processing Example:")
    print("=" * 40)
    
    from src.speech.speech_generator import TechnicalTermHandler
    
    term_handler = TechnicalTermHandler()
    
    math_text = "Solve this quadratic equation using the coefficient method."
    processed_text = term_handler.process_technical_terms(math_text, "Hindi", "Mathematics")
    
    print(f"Original: {math_text}")
    print(f"Processed: {processed_text}")
    print()
    
    science_text = "The molecule contains multiple atoms bonded together."
    processed_text = term_handler.process_technical_terms(science_text, "Tamil", "Science")
    
    print(f"Original: {science_text}")
    print(f"Processed: {processed_text}")
    print()
    
    # Demonstrate audio quality validation
    print("Audio Quality Validation Example:")
    print("=" * 40)
    
    # Create a mock audio file for demonstration
    mock_audio = AudioFile(
        content=b"mock_audio_content_for_demonstration",
        format="mp3",
        size_mb=2.5,
        duration_seconds=45.0,
        sample_rate=22050,
        language="Hindi",
        accuracy_score=0.94
    )
    
    is_valid = speech_generator.validate_audio_quality(mock_audio)
    print(f"Audio file validation: {'✓ PASSED' if is_valid else '❌ FAILED'}")
    print(f"Size: {mock_audio.size_mb} MB")
    print(f"Duration: {mock_audio.duration_seconds} seconds")
    print(f"Accuracy: {mock_audio.accuracy_score:.1%}")
    print()
    
    # Show quality requirements
    print("Quality Requirements:")
    print("- File size: ≤ 5 MB (optimized for low-end devices)")
    print("- Audio accuracy: ≥ 90% (ASR validation)")
    print("- Format: MP3 (compressed for bandwidth efficiency)")
    print("- Sample rate: 22050 Hz (optimized for speech)")
    print("- Channels: Mono (smaller file size)")
    print()
    
    print("Example completed! 🎉")
    print("\nTo use the Speech Generator in your application:")
    print("1. Initialize: speech_generator = SpeechGenerator()")
    print("2. Generate: audio_file = speech_generator.generate_speech(text, language, subject)")
    print("3. Validate: is_valid = speech_generator.validate_audio_quality(audio_file)")


if __name__ == "__main__":
    main()