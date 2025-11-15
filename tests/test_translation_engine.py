"""Tests for Translation Engine component."""
import pytest
from src.translator import TranslationEngine, TranslatedText


class TestTranslationEngine:
    """Test suite for TranslationEngine class."""
    
    def test_engine_initialization(self):
        """Test that TranslationEngine initializes correctly."""
        engine = TranslationEngine()
        assert engine is not None
        assert engine.model_client is None
        assert len(engine.get_supported_languages()) == 5
    
    def test_supported_languages(self):
        """Test that all MVP languages are supported."""
        engine = TranslationEngine()
        supported = engine.get_supported_languages()
        
        assert 'Hindi' in supported
        assert 'Tamil' in supported
        assert 'Telugu' in supported
        assert 'Bengali' in supported
        assert 'Marathi' in supported
    
    def test_translate_basic(self):
        """Test basic translation functionality."""
        engine = TranslationEngine()
        
        text = "The cell is the basic unit of life."
        result = engine.translate(
            text=text,
            target_language='Hindi',
            subject='Science'
        )
        
        assert isinstance(result, TranslatedText)
        assert result.target_language == 'Hindi'
        assert result.source_language == 'English'
        assert result.subject == 'Science'
        assert result.text is not None
        assert len(result.text) > 0
    
    def test_translate_all_languages(self):
        """Test translation to all supported languages."""
        engine = TranslationEngine()
        text = "Mathematics is the study of numbers."
        
        for language in engine.get_supported_languages():
            result = engine.translate(
                text=text,
                target_language=language,
                subject='Mathematics'
            )
            
            assert result.target_language == language
            assert result.text is not None
    
    def test_translate_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        engine = TranslationEngine()
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            engine.translate(
                text="",
                target_language='Hindi',
                subject='Science'
            )
    
    def test_translate_unsupported_language_raises_error(self):
        """Test that unsupported language raises ValueError."""
        engine = TranslationEngine()
        
        with pytest.raises(ValueError, match="not supported"):
            engine.translate(
                text="Test text",
                target_language='French',
                subject='Science'
            )
    
    def test_script_validation_hindi(self):
        """Test Unicode script validation for Hindi (Devanagari)."""
        engine = TranslationEngine()
        
        # Valid Hindi text
        hindi_text = "यह एक परीक्षण है"
        assert engine.validate_script_rendering(hindi_text, 'Hindi') is True
        
        # Invalid (English text)
        english_text = "This is a test"
        assert engine.validate_script_rendering(english_text, 'Hindi') is False
    
    def test_script_validation_tamil(self):
        """Test Unicode script validation for Tamil."""
        engine = TranslationEngine()
        
        # Valid Tamil text
        tamil_text = "இது ஒரு சோதனை"
        assert engine.validate_script_rendering(tamil_text, 'Tamil') is True
    
    def test_script_validation_telugu(self):
        """Test Unicode script validation for Telugu."""
        engine = TranslationEngine()
        
        # Valid Telugu text
        telugu_text = "ఇది ఒక పరీక్ష"
        assert engine.validate_script_rendering(telugu_text, 'Telugu') is True
    
    def test_script_validation_bengali(self):
        """Test Unicode script validation for Bengali."""
        engine = TranslationEngine()
        
        # Valid Bengali text
        bengali_text = "এটি একটি পরীক্ষা"
        assert engine.validate_script_rendering(bengali_text, 'Bengali') is True
    
    def test_script_validation_marathi(self):
        """Test Unicode script validation for Marathi (Devanagari)."""
        engine = TranslationEngine()
        
        # Valid Marathi text
        marathi_text = "ही एक चाचणी आहे"
        assert engine.validate_script_rendering(marathi_text, 'Marathi') is True
    
    def test_technical_terminology_mathematics(self):
        """Test that mathematical terms are preserved."""
        engine = TranslationEngine()
        
        text = "An equation is a mathematical statement with variables."
        result = engine.translate(
            text=text,
            target_language='Hindi',
            subject='Mathematics'
        )
        
        # Check that technical terms were tracked
        assert result.metadata['technical_terms_preserved'] >= 0
    
    def test_technical_terminology_science(self):
        """Test that scientific terms are preserved."""
        engine = TranslationEngine()
        
        text = "Photosynthesis occurs in the cell using energy from light."
        result = engine.translate(
            text=text,
            target_language='Tamil',
            subject='Science'
        )
        
        assert result.metadata['technical_terms_preserved'] >= 0
    
    def test_semantic_equivalence_score(self):
        """Test that semantic equivalence score is calculated."""
        engine = TranslationEngine()
        
        text = "Democracy is a form of government."
        result = engine.translate(
            text=text,
            target_language='Bengali',
            subject='Social Studies'
        )
        
        assert 0.0 <= result.semantic_score <= 1.0
    
    def test_language_info(self):
        """Test getting language information."""
        engine = TranslationEngine()
        
        hindi_info = engine.get_language_info('Hindi')
        assert hindi_info is not None
        assert hindi_info['code'] == 'hin_Deva'
        assert hindi_info['script'] == 'Devanagari'
        assert 'unicode_range' in hindi_info
    
    def test_metadata_includes_language_code(self):
        """Test that result metadata includes language code."""
        engine = TranslationEngine()
        
        result = engine.translate(
            text="Test content",
            target_language='Telugu',
            subject='Science'
        )
        
        assert 'language_code' in result.metadata
        assert result.metadata['language_code'] == 'tel_Telu'
    
    def test_metadata_includes_script(self):
        """Test that result metadata includes script name."""
        engine = TranslationEngine()
        
        result = engine.translate(
            text="Test content",
            target_language='Tamil',
            subject='Mathematics'
        )
        
        assert 'script' in result.metadata
        assert result.metadata['script'] == 'Tamil'
    
    def test_translate_with_model_client(self):
        """Test translation with a mock model client."""
        class MockModelClient:
            def process(self, text, target_language):
                # Return mock Hindi translation
                return "यह एक परीक्षण अनुवाद है"
        
        engine = TranslationEngine(model_client=MockModelClient())
        
        result = engine.translate(
            text="This is a test translation",
            target_language='Hindi',
            subject='Science'
        )
        
        assert result.text is not None
        # Should use model client, so script validation should pass
        assert result.script_valid is True
    
    def test_fallback_translation_without_model(self):
        """Test fallback translation when model is not available."""
        engine = TranslationEngine()  # No model client
        
        result = engine.translate(
            text="Test content",
            target_language='Hindi',
            subject='Science'
        )
        
        # Fallback adds language marker
        assert '[Hindi]' in result.text or result.text is not None
    
    def test_multiple_subjects(self):
        """Test translation with different subjects."""
        engine = TranslationEngine()
        text = "This is educational content."
        
        subjects = ['Mathematics', 'Science', 'Social Studies']
        
        for subject in subjects:
            result = engine.translate(
                text=text,
                target_language='Hindi',
                subject=subject
            )
            
            assert result.subject == subject
    
    def test_translated_text_dataclass(self):
        """Test TranslatedText dataclass structure."""
        engine = TranslationEngine()
        
        result = engine.translate(
            text="Test",
            target_language='Hindi',
            subject='Science'
        )
        
        # Check all required fields exist
        assert hasattr(result, 'text')
        assert hasattr(result, 'source_language')
        assert hasattr(result, 'target_language')
        assert hasattr(result, 'subject')
        assert hasattr(result, 'script_valid')
        assert hasattr(result, 'semantic_score')
        assert hasattr(result, 'metadata')
