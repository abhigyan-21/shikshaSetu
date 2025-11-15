#!/bin/bash
# Deployment script for Hugging Face Spaces

set -e

echo "🚀 Starting deployment to Hugging Face Spaces..."

# Check if HF CLI is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "❌ Hugging Face CLI not found. Installing..."
    pip install huggingface_hub
fi

# Check if logged in
if ! huggingface-cli whoami &> /dev/null; then
    echo "❌ Not logged in to Hugging Face. Please run: huggingface-cli login"
    exit 1
fi

# Configuration
SPACE_NAME="${HF_SPACE_NAME:-education-content-pipeline}"
HF_USERNAME="${HF_USERNAME}"

if [ -z "$HF_USERNAME" ]; then
    echo "❌ HF_USERNAME environment variable not set"
    exit 1
fi

SPACE_REPO="https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"

echo "📦 Preparing deployment files..."

# Create temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Using temporary directory: $DEPLOY_DIR"

# Copy necessary files
cp -r src/ "$DEPLOY_DIR/"
cp -r alembic/ "$DEPLOY_DIR/"
cp alembic.ini "$DEPLOY_DIR/"
cp init-db.sql "$DEPLOY_DIR/"
cp deployment/huggingface/Dockerfile "$DEPLOY_DIR/"
cp deployment/huggingface/requirements.txt "$DEPLOY_DIR/"
cp deployment/huggingface/README.md "$DEPLOY_DIR/"

# Create .env.example for documentation
cat > "$DEPLOY_DIR/.env.example" << EOF
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/dbname
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=education_content

# Hugging Face API
HUGGINGFACE_API_KEY=your_hf_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=false

# Model IDs
FLANT5_MODEL_ID=google/flan-t5-base
INDICTRANS2_MODEL_ID=ai4bharat/indictrans2-en-indic-1B
BERT_MODEL_ID=bert-base-multilingual-cased
VITS_MODEL_ID=facebook/mms-tts-hin

# Optional: Bhashini API
BHASHINI_API_KEY=
BHASHINI_API_URL=https://dhruva-api.bhashini.gov.in/services/inference/pipeline

# Rate Limiting
RATE_LIMIT_CALLS=100
RATE_LIMIT_WINDOW=60
EOF

echo "🔄 Cloning Space repository..."
cd "$DEPLOY_DIR"
git init
git remote add origin "$SPACE_REPO"

# Try to pull existing content
git pull origin main 2>/dev/null || echo "Creating new Space..."

echo "📝 Committing changes..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"

echo "⬆️  Pushing to Hugging Face Spaces..."
git push -u origin main

echo "✅ Deployment complete!"
echo "🌐 Your Space will be available at: $SPACE_REPO"
echo ""
echo "⚠️  Don't forget to configure secrets in Space settings:"
echo "   - DATABASE_URL"
echo "   - HUGGINGFACE_API_KEY"
echo "   - FLASK_SECRET_KEY"
echo "   - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB"

# Cleanup
cd -
rm -rf "$DEPLOY_DIR"
