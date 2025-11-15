"""Tests for TextSimplifier component."""
import pytest
from src.simplifier import TextSimplifier, SimplifiedText, ComplexityAnalyzer


class TestTextSimplifier:
    """Test TextSimplifier functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.simplifier = TextSimplifier()
    
    def test_simplifier_initialization(self):
        """Test that simplifier initializes correctly."""
        assert self.simplifier is not None
        assert self.simplifier.model_client is None
    
    def test_simplify_text_basic(self):
        """Test basic text simplification."""
        content = "Photosynthesis is the biochemical process by which plants convert light energy into chemical energy."
        result = self.simplifier.simplify_text(content, grade_level=8, subject="Science")
        
        assert isinstance(result, SimplifiedText)
        assert result.text is not None
        assert len(result.text) > 0
        assert result.grade_level == 8
        assert result.subject == "Science"
        assert 0 <= result.complexity_score <= 1
    
    def test_simplify_text_grade_5(self):
        """Test simplification for grade 5."""
        content = "The mitochondria are organelles that generate most of the cell's supply of adenosine triphosphate."
        result = self.simplifier.simplify_text(content, grade_level=5, subject="Science")
        
        assert result.grade_level == 5
        assert result.complexity_score < 0.5  # Should be simpler for grade 5
    
    def test_simplify_text_grade_12(self):
        """Test simplification for grade 12."""
        content = "The derivative of a function represents the rate of change."
        result = self.simplifier.simplify_text(content, grade_level=12, subject="Mathematics")
        
        assert result.grade_level == 12
        # Grade 12 content can maintain higher complexity
    
    def test_simplify_empty_content_raises_error(self):
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            self.simplifier.simplify_text("", grade_level=8, subject="Science")
        assert "Content cannot be empty" in str(exc_info.value)
    
    def test_simplify_invalid_grade_level_raises_error(self):
        """Test that invalid grade level raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            self.simplifier.simplify_text("Sample content", grade_level=3, subject="Science")
        assert "Grade level must be between 5 and 12" in str(exc_info.value)
    
    def test_complexity_score_calculation(self):
        """Test complexity score calculation."""
        simple_text = "The cat sat on the mat. It was a sunny day."
        complex_text = "The implementation of sophisticated algorithms necessitates comprehensive understanding of computational complexity theory."
        
        simple_score = self.simplifier.get_complexity_score(simple_text)
        complex_score = self.simplifier.get_complexity_score(complex_text)
        
        assert simple_score < complex_score
        assert 0 <= simple_score <= 1
        assert 0 <= complex_score <= 1
    
    def test_subject_specific_simplification_math(self):
        """Test subject-specific simplification for Mathematics."""
        content = "The quadratic equation ax² + bx + c = 0 has solutions determined by the discriminant."
        result = self.simplifier.simplify_text(content, grade_level=10, subject="Mathematics")
        
        assert result.subject == "Mathematics"
        assert result.text is not None
    
    def test_subject_specific_simplification_science(self):
        """Test subject-specific simplification for Science."""
        content = "Cellular respiration involves glycolysis, the Krebs cycle, and oxidative phosphorylation."
        result = self.simplifier.simplify_text(content, grade_level=9, subject="Science")
        
        assert result.subject == "Science"
        assert result.text is not None
    
    def test_metadata_includes_original_complexity(self):
        """Test that metadata includes original complexity score."""
        content = "Sample educational content for testing purposes."
        result = self.simplifier.simplify_text(content, grade_level=8, subject="Science")
        
        assert 'original_complexity' in result.metadata
        assert 'target_complexity_range' in result.metadata
        assert 'simplification_method' in result.metadata


class TestComplexityAnalyzer:
    """Test ComplexityAnalyzer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ComplexityAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly."""
        assert self.analyzer is not None
    
    def test_analyze_simple_text(self):
        """Test analysis of simple text."""
        text = "The cat sat on the mat. It was a sunny day."
        metrics = self.analyzer.analyze(text)
        
        assert metrics.total_sentences == 2
        assert metrics.total_words > 0
        assert 0 <= metrics.complexity_score <= 1
        assert metrics.readability_level in ['Very Easy', 'Easy', 'Moderate']
    
    def test_analyze_complex_text(self):
        """Test analysis of complex text."""
        text = "The implementation of sophisticated algorithms necessitates comprehensive understanding of computational complexity theory and advanced mathematical concepts."
        metrics = self.analyzer.analyze(text)
        
        assert metrics.total_sentences == 1
        assert metrics.total_words > 0
        assert metrics.complexity_score > 0.5
        assert metrics.readability_level in ['Moderate', 'Difficult', 'Very Difficult']
    
    def test_analyze_empty_text(self):
        """Test analysis of empty text."""
        metrics = self.analyzer.analyze("")
        
        assert metrics.total_sentences == 0
        assert metrics.total_words == 0
        assert metrics.complexity_score == 0.0
    
    def test_grade_level_recommendation(self):
        """Test grade level recommendation based on complexity."""
        # Simple text should recommend lower grade
        simple_score = 0.3
        grade = self.analyzer.get_grade_level_recommendation(simple_score)
        assert 5 <= grade <= 7
        
        # Complex text should recommend higher grade
        complex_score = 0.8
        grade = self.analyzer.get_grade_level_recommendation(complex_score)
        assert 10 <= grade <= 12
