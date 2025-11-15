# Hugging Face Spaces Deployment

This directory contains configuration files for deploying the Multilingual Education Content Pipeline to Hugging Face Spaces.

## Prerequisites

1. Hugging Face account with Spaces enabled
2. Hugging Face API token with write access
3. PostgreSQL database (external or managed service)

## Deployment Steps

### 1. Create a New Space

```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login to Hugging Face
huggingface-cli login

# Create a new Space
huggingface-cli repo create --type space --space_sdk docker education-content-pipeline
```

### 2. Configure Secrets

In your Hugging Face Space settings, add the following secrets:

- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `DATABASE_URL`: Full PostgreSQL connection string
- `HUGGINGFACE_API_KEY`: Your HF API key for model inference
- `FLASK_SECRET_KEY`: Random secret key for Flask sessions
- `BHASHINI_API_KEY`: (Optional) Bhashini TTS API key

### 3. Deploy to Space

```bash
# Clone your Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/education-content-pipeline
cd education-content-pipeline

# Copy deployment files
cp -r deployment/huggingface/* .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

## Space Configuration

The Space uses Docker SDK with the following configuration:

- **SDK**: Docker
- **Hardware**: CPU Basic (upgrade to GPU for faster inference)
- **Persistent Storage**: Enabled (for content caching)
- **Port**: 7860 (default for Spaces)

## Monitoring

Access logs and metrics through:
- Hugging Face Space logs tab
- Prometheus metrics at `/metrics` endpoint
- Grafana dashboard (if configured)

## Scaling Considerations

For production workloads:
1. Upgrade to GPU hardware for faster model inference
2. Enable persistent storage for content caching
3. Configure external PostgreSQL with read replicas
4. Set up CDN for static assets
5. Implement rate limiting and authentication
