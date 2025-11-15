"""Setup script for the education content pipeline."""
from setuptools import setup, find_packages

setup(
    name="education-content-pipeline",
    version="1.0.0",
    description="AI-powered multilingual education content pipeline",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "flask>=3.0.0",
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "flask-cors>=4.0.0",
        "sqlalchemy>=2.0.23",
        "psycopg2-binary>=2.9.9",
        "alembic>=1.12.1",
        "requests>=2.31.0",
        "pydantic>=2.5.0",
        "transformers>=4.35.2",
        "torch>=2.1.1",
        "sentencepiece>=0.1.99",
        "soundfile>=0.12.1",
        "librosa>=0.10.1",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
        ]
    },
)
