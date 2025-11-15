"""Example usage of TextSimplifier component."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.simplifier import TextSimplifier, ComplexityAnalyzer


def main():
    """Demonstrate TextSimplifier functionality."""
    
    # Initialize simplifier
    simplifier = TextSimplifier()
    analyzer = ComplexityAnalyzer()
    
    # Sample educational content
    content = """
    Photosynthesis is the biochemical process by which green plants, algae, and certain bacteria 
    convert light energy, usually from the sun, into chemical energy stored in glucose molecules. 
    This process occurs primarily in the chloroplasts of plant cells and involves two main stages: 
    the light-dependent reactions and the light-independent reactions (Calvin cycle). During the 
    light-dependent reactions, chlorophyll absorbs photons and uses this energy to split water 
    molecules, releasing oxygen as a byproduct and generating ATP and NADPH. These energy carriers 
    are then utilized in the Calvin cycle to fix carbon dioxide from the atmosphere into organic 
    compounds, ultimately producing glucose.
    """
    
    print("=" * 80)
    print("TEXT SIMPLIFIER DEMONSTRATION")
    print("=" * 80)
    
    # Analyze original complexity
    print("\n1. ORIGINAL CONTENT ANALYSIS")
    print("-" * 80)
    original_metrics = analyzer.analyze(content)
    print(f"Total Sentences: {original_metrics.total_sentences}")
    print(f"Total Words: {original_metrics.total_words}")
    print(f"Avg Sentence Length: {original_metrics.avg_sentence_length:.1f} words")
    print(f"Avg Word Length: {original_metrics.avg_word_length:.1f} characters")
    print(f"Avg Syllables/Word: {original_metrics.avg_syllables_per_word:.1f}")
    print(f"Complexity Score: {original_metrics.complexity_score:.2f}")
    print(f"Readability Level: {original_metrics.readability_level}")
    print(f"Recommended Grade: {analyzer.get_grade_level_recommendation(original_metrics.complexity_score)}")
    
    # Simplify for different grade levels
    grade_levels = [5, 8, 12]
    subjects = ["Science", "Science", "Science"]
    
    for grade, subject in zip(grade_levels, subjects):
        print(f"\n2. SIMPLIFICATION FOR GRADE {grade} ({subject})")
        print("-" * 80)
        
        result = simplifier.simplify_text(content, grade_level=grade, subject=subject)
        
        print(f"Grade Level: {result.grade_level}")
        print(f"Subject: {result.subject}")
        print(f"Complexity Score: {result.complexity_score:.2f}")
        print(f"Original Complexity: {result.metadata['original_complexity']:.2f}")
        print(f"Target Range: {result.metadata['target_complexity_range']}")
        print(f"Method: {result.metadata['simplification_method']}")
        print(f"\nSimplified Text Preview:")
        print(result.text[:200] + "..." if len(result.text) > 200 else result.text)
    
    # Demonstrate subject-specific simplification
    print("\n3. SUBJECT-SPECIFIC SIMPLIFICATION")
    print("-" * 80)
    
    math_content = "The quadratic equation ax² + bx + c = 0 can be solved using the quadratic formula: x = (-b ± √(b² - 4ac)) / 2a"
    math_result = simplifier.simplify_text(math_content, grade_level=10, subject="Mathematics")
    
    print("Mathematics Content:")
    print(f"Original: {math_content}")
    print(f"Simplified: {math_result.text}")
    print(f"Complexity: {math_result.complexity_score:.2f}")
    
    # Demonstrate complexity scoring
    print("\n4. COMPLEXITY SCORING EXAMPLES")
    print("-" * 80)
    
    examples = [
        ("The cat sat on the mat.", "Very Simple"),
        ("Water is essential for all living organisms.", "Simple"),
        ("The implementation requires careful consideration of multiple factors.", "Moderate"),
        ("The epistemological implications of quantum mechanics necessitate comprehensive analysis.", "Complex")
    ]
    
    for text, description in examples:
        score = simplifier.get_complexity_score(text)
        print(f"{description:15} (Score: {score:.2f}): {text}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
