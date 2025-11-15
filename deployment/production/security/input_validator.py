"""
Input Validation and Sanitization
Validates and sanitizes all user inputs to prevent security vulnerabilities
"""
import re
from typing import Dict, Any, List, Optional
from werkzeug.utils import secure_filename
import bleach

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Supported languages
SUPPORTED_LANGUAGES = [
    'hindi', 'tamil', 'telugu', 'bengali', 'marathi',
    'gujarati', 'kannada', 'malayalam', 'punjabi', 'odia'
]

# Valid grade levels
VALID_GRADES = list(range(5, 13))  # 5-12

# Valid subjects
VALID_SUBJECTS = [
    'mathematics', 'science', 'social_studies', 'english',
    'physics', 'chemistry', 'biology', 'history', 'geography'
]

# Valid output formats
VALID_OUTPUT_FORMATS = ['text', 'audio', 'both']


class InputValidator:
    """Validates and sanitizes user inputs"""
    
    @staticmethod
    def validate_content_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content processing request parameters"""
        errors = []
        
        # Validate target language
        language = data.get('target_language', '').lower()
        if language not in SUPPORTED_LANGUAGES:
            errors.append(f"Invalid language. Supported: {', '.join(SUPPORTED_LANGUAGES)}")
        
        # Validate grade level
        grade = data.get('grade_level')
        try:
            grade = int(grade)
            if grade not in VALID_GRADES:
                errors.append(f"Invalid grade level. Must be between 5-12")
        except (ValueError, TypeError):
            errors.append("Grade level must be an integer")
        
        # Validate subject
        subject = data.get('subject', '').lower()
        if subject not in VALID_SUBJECTS:
            errors.append(f"Invalid subject. Supported: {', '.join(VALID_SUBJECTS)}")
        
        # Validate output format
        output_format = data.get('output_format', '').lower()
        if output_format not in VALID_OUTPUT_FORMATS:
            errors.append(f"Invalid output format. Must be: {', '.join(VALID_OUTPUT_FORMATS)}")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return {
            'target_language': language,
            'grade_level': grade,
            'subject': subject,
            'output_format': output_format
        }

    
    @staticmethod
    def validate_file_upload(file) -> bool:
        """Validate uploaded file"""
        if not file or not file.filename:
            raise ValueError("No file provided")
        
        # Check file extension
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > MAX_FILE_SIZE:
            raise ValueError(f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB")
        
        return True
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 50000) -> str:
        """Sanitize text input"""
        if not text:
            raise ValueError("Text content is required")
        
        # Remove HTML tags and scripts
        text = bleach.clean(text, tags=[], strip=True)
        
        # Limit length
        if len(text) > max_length:
            raise ValueError(f"Text too long. Maximum length: {max_length} characters")
        
        return text.strip()
