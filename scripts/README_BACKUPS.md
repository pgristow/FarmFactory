# FarmFactory Import Data Backup Strategy

## Overview

This document describes the backup strategy for FarmFactory import data, including uploaded files and import metadata.

## Backup Components

### 1. Uploaded Files
- **Location**: `./uploads/` directory
- **Contents**:
  - `staging/` - Temporary upload files
  - `processed/` - Successfully imported files
  - `failed/` - Failed import files with error logs
- **Format**: Compressed tarball (`.tar.gz`)

### 2. Import Metadata
- **Source**: PostgreSQL database
- **Tables**:
  - `import_jobs` - Import job tracking
  - `import_errors` - Row-level error details
  - `import_templates` - Saved column mappings
- **Format**: SQL dump

## Retention Policy

| Data Type | Retention Period | Location |
|-----------|------------------|----------|
| Upload files (staging) | 30 days | `uploads/staging/` |
| Upload files (processed) | 30 days | `uploads/processed/` |
| Upload files (failed) | 30 days | `uploads/failed/` |
| Backup archives | 30 days | `backups/imports/` |
| Import metadata (DB) | 90 days | PostgreSQL database |

## Automated Backups

### Celery Scheduled Tasks

Automatic cleanup tasks run via Celery Beat:

1. **File Cleanup** (Daily at 2:00 AM)
   - Task: `app.tasks.cleanup_tasks.cleanup_old_files`
   - Removes files older than 30 days
   - Affects: `uploads/staging/`, `uploads/processed/`, `uploads/failed/`

2. **Import Job Cleanup** (Weekly on Sunday at 3:00 AM)
   - Task: `app.tasks.cleanup_tasks.cleanup_old_import_jobs`
   - Removes import job records older than 90 days
   - Affects: `import_jobs`, `import_errors` tables

### Manual Backup Script

Location: `scripts/backup-imports.sh`

**Usage:**
```bash
# Run manual backup with default settings (30-day retention)
make backup-uploads

# Or run directly
./scripts/backup-imports.sh

# Custom retention period
./scripts/backup-imports.sh --retention-days 60
```

**What it backs up:**
- All files in `uploads/` directory (compressed)
- Import metadata from database tables
- Creates a manifest file with backup details

**Backup location:**
```
backups/imports/
└── import_backup_YYYYMMDD_HHMMSS/
    ├── uploads.tar.gz           # Compressed upload files
    ├── import_metadata.sql      # Database metadata
    └── manifest.txt             # Backup details
```

## Restore Procedures

### Restore Uploaded Files

```bash
# 1. List available backups
ls -lh backups/imports/

# 2. Extract files from backup
tar -xzf backups/imports/import_backup_YYYYMMDD_HHMMSS/uploads.tar.gz -C ./uploads/

# 3. Verify restoration
ls -lR ./uploads/
```

### Restore Import Metadata

```bash
# 1. Stop import processing
docker-compose stop celery_worker celery_beat

# 2. Restore database tables
docker-compose exec -T postgres psql -U $POSTGRES_USER -d $POSTGRES_DB \
    < backups/imports/import_backup_YYYYMMDD_HHMMSS/import_metadata.sql

# 3. Restart services
docker-compose start celery_worker celery_beat
```

### Full System Restore

```bash
# 1. Run database backup restore (see above)
# 2. Run file restore (see above)
# 3. Restart all services
make restart
```

## Monitoring Backups

### Check Storage Statistics

```bash
# Via Makefile
make storage-stats

# Via Python
docker-compose exec backend python -c \
    "from app.core.storage import storage_service; \
     import json; \
     print(json.dumps(storage_service.get_storage_stats(), indent=2))"
```

### Manual Cleanup

```bash
# Trigger cleanup manually
make storage-cleanup

# Via Python
docker-compose exec backend python -c \
    "from app.core.storage import storage_service; \
     import json; \
     print(json.dumps(storage_service.cleanup_old_files(), indent=2))"
```

## Backup Best Practices

### Development Environment

1. **Test Restores Regularly**
   - Verify backup integrity by performing test restores
   - Schedule quarterly restore tests

2. **Monitor Disk Space**
   - Check available disk space before large imports
   - Set up alerts for low disk space (< 20% free)

3. **Document Import Issues**
   - Save failed import files for debugging
   - Review error patterns to improve validation

### Production Environment

1. **Offsite Backups**
   - Copy backups to external storage (S3, Google Cloud Storage)
   - Use `rsync` or cloud sync tools

2. **Encryption**
   - Encrypt backups containing sensitive data
   - Use GPG or cloud provider encryption

3. **Backup Verification**
   - Automate backup integrity checks
   - Test restore procedures monthly

4. **Disaster Recovery Plan**
   - Document recovery time objectives (RTO)
   - Define recovery point objectives (RPO)
   - Maintain runbook for emergency recovery

## Cron Setup (Optional)

For automated backups outside of Docker:

```bash
# Add to crontab
crontab -e

# Run daily backup at 1:00 AM
0 1 * * * /path/to/farmfactory/scripts/backup-imports.sh >> /var/log/farmfactory/backup.log 2>&1

# Run weekly full system backup on Sunday at 2:00 AM
0 2 * * 0 /path/to/farmfactory/scripts/full-backup.sh >> /var/log/farmfactory/backup.log 2>&1
```

## Backup Size Estimates

Based on typical usage:

| Import Volume | Daily Upload Size | Monthly Backup Size |
|---------------|-------------------|---------------------|
| Light (10 imports/day) | ~500 MB | ~15 GB |
| Medium (50 imports/day) | ~2.5 GB | ~75 GB |
| Heavy (200 imports/day) | ~10 GB | ~300 GB |

**Note**: Compression typically reduces size by 60-80% for CSV/Excel files.

## Troubleshooting

### Backup Failures

**Issue**: Backup script fails with "permission denied"
```bash
# Solution: Fix permissions
chmod +x scripts/backup-imports.sh
sudo chown -R $(whoami) backups/
```

**Issue**: Database dump fails
```bash
# Solution: Check PostgreSQL connection
docker-compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1"
```

**Issue**: Out of disk space
```bash
# Solution: Clean up old backups manually
find backups/imports/ -type d -mtime +30 -exec rm -rf {} +

# Or increase retention period
./scripts/backup-imports.sh --retention-days 7
```

### Restore Failures

**Issue**: Import tables don't exist
```bash
# Solution: Run migrations first
make migrate
# Then restore
```

**Issue**: Duplicate key errors during restore
```bash
# Solution: Clear existing data first
docker-compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB \
    -c "TRUNCATE import_jobs, import_errors, import_templates CASCADE"
# Then restore
```

## Support

For backup-related issues:
1. Check logs: `docker-compose logs celery_worker`
2. Review backup manifest: `cat backups/imports/*/manifest.txt`
3. Contact DevOps team or raise an issue

## References

- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [Docker Volume Backups](https://docs.docker.com/storage/volumes/#backup-restore-or-migrate-data-volumes)
- [Celery Beat Scheduling](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html)
