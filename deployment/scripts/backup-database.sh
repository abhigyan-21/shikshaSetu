#!/bin/bash
# Database Backup Script
# Creates automated backups of PostgreSQL database with rotation

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/education-content}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="education_content_backup_${TIMESTAMP}.sql.gz"

# Database connection (from environment or defaults)
DB_HOST="${POSTGRES_HOST:-postgres_primary}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-education_content}"
DB_USER="${POSTGRES_USER:-postgres}"

echo "🗄️  Starting database backup..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform backup
echo "📦 Creating backup: $BACKUP_FILE"
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --format=plain \
    --no-owner \
    --no-acl \
    --verbose \
    2>&1 | gzip > "$BACKUP_DIR/$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    echo "✅ Backup completed successfully: $BACKUP_FILE ($BACKUP_SIZE)"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Verify backup integrity
echo "🔍 Verifying backup integrity..."
gunzip -t "$BACKUP_DIR/$BACKUP_FILE"
if [ $? -eq 0 ]; then
    echo "✅ Backup integrity verified"
else
    echo "❌ Backup verification failed!"
    exit 1
fi

# Rotate old backups
echo "🔄 Rotating old backups (keeping last $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "education_content_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
REMAINING_BACKUPS=$(find "$BACKUP_DIR" -name "education_content_backup_*.sql.gz" -type f | wc -l)
echo "✅ Backup rotation complete. $REMAINING_BACKUPS backups remaining."

# Optional: Upload to cloud storage (uncomment and configure as needed)
# if [ -n "$AWS_S3_BUCKET" ]; then
#     echo "☁️  Uploading to S3..."
#     aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" "s3://$AWS_S3_BUCKET/backups/"
#     echo "✅ Uploaded to S3"
# fi

echo "✅ Backup process complete!"
echo "📍 Backup location: $BACKUP_DIR/$BACKUP_FILE"
