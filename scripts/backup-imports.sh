#!/bin/bash

################################################################################
# FarmFactory Import Data Backup Script
#
# This script backs up uploaded files and import metadata.
# Retention: 30 days for backup files
#
# Usage:
#   ./scripts/backup-imports.sh [--retention-days DAYS]
#
# Environment Variables:
#   BACKUP_DIR: Directory to store backups (default: ./backups/imports)
#   RETENTION_DAYS: Number of days to keep backups (default: 30)
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups/imports}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="import_backup_${TIMESTAMP}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --retention-days)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--retention-days DAYS]"
            echo ""
            echo "Options:"
            echo "  --retention-days DAYS   Number of days to keep backups (default: 30)"
            echo "  --help                  Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Functions
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
create_backup_dir() {
    log_info "Creating backup directory: $BACKUP_DIR/$BACKUP_NAME"
    mkdir -p "$BACKUP_DIR/$BACKUP_NAME"
}

# Backup uploaded files
backup_uploads() {
    log_info "Backing up uploaded files..."

    local upload_dir="$PROJECT_ROOT/uploads"

    if [ ! -d "$upload_dir" ]; then
        log_warning "Upload directory not found: $upload_dir"
        return 0
    fi

    # Count files
    local total_files=$(find "$upload_dir" -type f | wc -l)
    local total_size=$(du -sh "$upload_dir" 2>/dev/null | cut -f1)

    if [ "$total_files" -eq 0 ]; then
        log_warning "No files to backup"
        return 0
    fi

    log_info "Found $total_files files (total size: $total_size)"

    # Create tarball of uploads directory
    tar -czf "$BACKUP_DIR/$BACKUP_NAME/uploads.tar.gz" \
        -C "$upload_dir" . \
        2>/dev/null || {
        log_error "Failed to create uploads tarball"
        return 1
    }

    local backup_size=$(du -sh "$BACKUP_DIR/$BACKUP_NAME/uploads.tar.gz" | cut -f1)
    log_success "Uploaded files backed up ($backup_size)"
}

# Backup import metadata from database
backup_import_metadata() {
    log_info "Backing up import metadata from database..."

    # Load environment variables
    if [ -f "$PROJECT_ROOT/.env" ]; then
        source "$PROJECT_ROOT/.env"
    else
        log_warning ".env file not found, using defaults"
        POSTGRES_USER="${POSTGRES_USER:-farm_user}"
        POSTGRES_DB="${POSTGRES_DB:-farmfactory}"
    fi

    # Export import-related tables
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T postgres \
        pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
        -t import_jobs -t import_errors -t import_templates \
        --clean --if-exists --no-owner \
        > "$BACKUP_DIR/$BACKUP_NAME/import_metadata.sql" 2>/dev/null || {
        log_warning "Failed to backup import metadata (tables may not exist yet)"
        return 0
    }

    local metadata_size=$(du -sh "$BACKUP_DIR/$BACKUP_NAME/import_metadata.sql" 2>/dev/null | cut -f1 || echo "0")
    log_success "Import metadata backed up ($metadata_size)"
}

# Create backup manifest
create_manifest() {
    log_info "Creating backup manifest..."

    local manifest_file="$BACKUP_DIR/$BACKUP_NAME/manifest.txt"

    cat > "$manifest_file" <<EOF
FarmFactory Import Data Backup
==============================

Backup Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Backup Name: $BACKUP_NAME
Retention Period: $RETENTION_DAYS days

Contents:
---------
EOF

    if [ -f "$BACKUP_DIR/$BACKUP_NAME/uploads.tar.gz" ]; then
        echo "- uploads.tar.gz (uploaded files)" >> "$manifest_file"
        echo "  Size: $(du -sh "$BACKUP_DIR/$BACKUP_NAME/uploads.tar.gz" | cut -f1)" >> "$manifest_file"
    fi

    if [ -f "$BACKUP_DIR/$BACKUP_NAME/import_metadata.sql" ]; then
        echo "- import_metadata.sql (database metadata)" >> "$manifest_file"
        echo "  Size: $(du -sh "$BACKUP_DIR/$BACKUP_NAME/import_metadata.sql" | cut -f1)" >> "$manifest_file"
    fi

    echo "" >> "$manifest_file"
    echo "Total Backup Size: $(du -sh "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)" >> "$manifest_file"

    log_success "Backup manifest created"
}

# Clean up old backups
cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."

    local deleted_count=0
    local freed_space=0

    # Find and delete old backups
    if [ -d "$BACKUP_DIR" ]; then
        while IFS= read -r -d '' backup; do
            local backup_size=$(du -sb "$backup" | cut -f1)
            rm -rf "$backup"
            ((deleted_count++))
            ((freed_space+=backup_size))
        done < <(find "$BACKUP_DIR" -maxdepth 1 -type d -name "import_backup_*" -mtime +$RETENTION_DAYS -print0)
    fi

    if [ $deleted_count -gt 0 ]; then
        local freed_mb=$((freed_space / 1024 / 1024))
        log_success "Deleted $deleted_count old backup(s), freed ${freed_mb}MB"
    else
        log_info "No old backups to clean up"
    fi
}

# List existing backups
list_backups() {
    log_info "Existing backups:"

    if [ ! -d "$BACKUP_DIR" ]; then
        log_warning "No backup directory found"
        return 0
    fi

    local backup_count=0
    while IFS= read -r -d '' backup; do
        local backup_name=$(basename "$backup")
        local backup_date=$(echo "$backup_name" | sed 's/import_backup_//' | sed 's/_/ /' | sed 's/\([0-9]\{8\}\)/\1 /')
        local backup_size=$(du -sh "$backup" | cut -f1)
        local backup_age=$(find "$backup" -maxdepth 0 -mtime +0 -printf '%Td days ago\n' || echo "Today")

        echo -e "  ${CYAN}$backup_name${NC}"
        echo -e "    Date: $backup_date"
        echo -e "    Size: $backup_size"
        echo -e "    Age:  $backup_age"
        ((backup_count++))
    done < <(find "$BACKUP_DIR" -maxdepth 1 -type d -name "import_backup_*" -print0 | sort -rz)

    if [ $backup_count -eq 0 ]; then
        log_warning "No backups found"
    else
        log_info "Total backups: $backup_count"
    fi
}

# Main execution
main() {
    echo -e "${CYAN}======================================${NC}"
    echo -e "${CYAN}FarmFactory Import Data Backup${NC}"
    echo -e "${CYAN}======================================${NC}"
    echo ""

    log_info "Starting backup process..."
    log_info "Timestamp: $TIMESTAMP"
    log_info "Retention: $RETENTION_DAYS days"
    echo ""

    # Create backup directory
    create_backup_dir

    # Perform backups
    backup_uploads
    backup_import_metadata

    # Create manifest
    create_manifest

    # Cleanup old backups
    echo ""
    cleanup_old_backups

    # Summary
    echo ""
    echo -e "${GREEN}======================================${NC}"
    log_success "Backup completed successfully!"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo "Backup location: $BACKUP_DIR/$BACKUP_NAME"
    echo "Total size: $(du -sh "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)"
    echo ""

    # List all backups
    list_backups

    echo ""
    echo -e "${CYAN}To restore from this backup:${NC}"
    echo -e "  1. Extract uploads: tar -xzf $BACKUP_DIR/$BACKUP_NAME/uploads.tar.gz -C ./uploads/"
    echo -e "  2. Restore metadata: docker-compose exec -T postgres psql -U \$POSTGRES_USER -d \$POSTGRES_DB < $BACKUP_DIR/$BACKUP_NAME/import_metadata.sql"
}

# Run main function
main "$@"
