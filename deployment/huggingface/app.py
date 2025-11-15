"""
Hugging Face Spaces Entry Point
This file serves as the main entry point for the HF Space deployment.
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.flask_app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)
