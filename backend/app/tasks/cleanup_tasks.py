"""
Cleanup Tasks

Periodic maintenance tasks for file and database cleanup.
"""

from celery import shared_task
from app.core.storage import storage_service
import logging

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.cleanup_tasks.cleanup_old_files", bind=True)
def cleanup_old_files(self, retention_days: int = 30):
    """
    Clean up old uploaded files based on retention policy

    Args:
        retention_days: Number of days to retain files (default: 30)

    Returns:
        Cleanup statistics
    """
    try:
        logger.info(f"Starting file cleanup with {retention_days} day retention")
        stats = storage_service.cleanup_old_files(retention_days)
        logger.info(
            f"Cleanup complete: Deleted {stats['deleted_count']} files, "
            f"freed {stats['freed_mb']} MB"
        )
        return stats
    except Exception as e:
        logger.error(f"Error during file cleanup: {str(e)}")
        raise


@shared_task(name="app.tasks.cleanup_tasks.cleanup_old_import_jobs", bind=True)
def cleanup_old_import_jobs(self, retention_days: int = 90):
    """
    Clean up old import job records from database

    Args:
        retention_days: Number of days to retain import job records (default: 90)

    Returns:
        Cleanup statistics
    """
    try:
        from datetime import datetime, timedelta
        from app.core.database import SessionLocal

        logger.info(f"Starting import job cleanup with {retention_days} day retention")

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # This will be implemented when import models are created
        # For now, just log
        logger.info(f"Would delete import jobs older than {cutoff_date}")

        stats = {
            "deleted_count": 0,
            "message": "Import job cleanup not yet implemented",
        }

        return stats
    except Exception as e:
        logger.error(f"Error during import job cleanup: {str(e)}")
        raise
