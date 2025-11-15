#!/bin/bash
# Production Environment Setup Script
# Sets up the production environment with all necessary configurations

set -e

echo "🚀 Setting up production environment..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script should be run as root or with sudo"
    exit 1
fi

# Configuration
DEPLOY_DIR="/opt/education-content-pipeline"
DATA_DIR="/var/lib/education-content"
LOG_DIR="/var/log/education-content"
SSL_DIR="/etc/nginx/ssl"

echo "📁 Creating directory structure..."
mkdir -p "$DEPLOY_DIR"
mkdir -p "$DATA_DIR"/{audio,cache,curriculum}
mkdir -p "$LOG_DIR"
mkdir -p "$SSL_DIR"

# Set permissions
chown -R www-data:www-data "$DATA_DIR"
chown -R www-data:www-data "$LOG_DIR"
chmod 755 "$DATA_DIR"
chmod 755 "$LOG_DIR"

echo "🔐 Generating SSL certificates (self-signed for testing)..."
if [ ! -f "$SSL_DIR/cert.pem" ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/key.pem" \
        -out "$SSL_DIR/cert.pem" \
        -subj "/C=IN/ST=State/L=City/O=Organization/CN=localhost"
    chmod 600 "$SSL_DIR/key.pem"
    chmod 644 "$SSL_DIR/cert.pem"
    echo "✅ Self-signed certificates generated"
    echo "⚠️  For production, replace with proper SSL certificates"
else
    echo "✅ SSL certificates already exist"
fi

echo "🐳 Installing Docker and Docker Compose..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

echo "📝 Creating environment file..."
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    cat > "$DEPLOY_DIR/.env" << 'EOF'
# Production Environment Configuration
# IMPORTANT: Update all passwords and secrets before deploying!

# Database Configuration
POSTGRES_DB=education_content
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD
REPLICATION_PASSWORD=CHANGE_THIS_PASSWORD
DATABASE_URL=postgresql://postgres:CHANGE_THIS_PASSWORD@postgres_primary:5432/education_content

# Flask Configuration
FLASK_SECRET_KEY=CHANGE_THIS_SECRET_KEY
FLASK_DEBUG=false

# Hugging Face API
HUGGINGFACE_API_KEY=YOUR_HF_API_KEY_HERE

# Model Configuration
FLANT5_MODEL_ID=google/flan-t5-base
INDICTRANS2_MODEL_ID=ai4bharat/indictrans2-en-indic-1B
BERT_MODEL_ID=bert-base-multilingual-cased
VITS_MODEL_ID=facebook/mms-tts-hin

# Redis
REDIS_URL=redis://redis:6379/0

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=CHANGE_THIS_PASSWORD

# Rate Limiting
RATE_LIMIT_CALLS=100
RATE_LIMIT_WINDOW=60
EOF
    echo "✅ Environment file created at $DEPLOY_DIR/.env"
    echo "⚠️  IMPORTANT: Edit $DEPLOY_DIR/.env and update all passwords and API keys!"
else
    echo "✅ Environment file already exists"
fi

echo "🔧 Setting up firewall rules..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    ufw allow 3000/tcp  # Grafana
    ufw allow 9090/tcp  # Prometheus
    ufw --force enable
    echo "✅ Firewall configured"
fi

echo "📊 Creating monitoring directories..."
mkdir -p "$DEPLOY_DIR/monitoring/grafana/dashboards"
mkdir -p "$DEPLOY_DIR/monitoring/grafana/datasources"
mkdir -p "$DEPLOY_DIR/monitoring/prometheus"

echo "✅ Production environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit $DEPLOY_DIR/.env and update all passwords and API keys"
echo "2. Copy your application code to $DEPLOY_DIR"
echo "3. Copy deployment configurations to $DEPLOY_DIR"
echo "4. Run: cd $DEPLOY_DIR && docker-compose -f deployment/production/docker-compose.prod.yml up -d"
echo "5. Monitor logs: docker-compose -f deployment/production/docker-compose.prod.yml logs -f"
echo ""
echo "Access points:"
echo "- Application: https://your-domain.com"
echo "- Grafana: http://your-domain.com:3000"
echo "- Prometheus: http://your-domain.com:9090"
