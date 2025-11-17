"""
Celery Application Configuration

Configures Celery for async task processing with Redis as broker.
Includes retry policies, task routing, and monitoring.
"""

import os
from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

# Get configuration from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://:redispass123@redis:6379/0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Create Celery application
celery_app = Celery(
    "farmfactory",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.import_tasks", "app.tasks.cleanup_tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution settings
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker dies
    task_track_started=True,  # Track when tasks start

    # Task time limits
    task_soft_time_limit=1800,  # 30 minutes soft limit
    task_time_limit=2400,  # 40 minutes hard limit

    # Retry settings
    task_default_retry_delay=60,  # Wait 60 seconds before retry
    task_max_retries=3,  # Maximum 3 retry attempts

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,  # Store extended task metadata

    # Worker settings
    worker_prefetch_multiplier=1,  # Only fetch one task at a time (for long tasks)
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (prevent memory leaks)

    # Monitoring
    worker_send_task_events=True,  # Send task events for monitoring
    task_send_sent_event=True,  # Send event when task is sent

    # Task routing - separate queues for different task types
    task_routes={
        "app.tasks.import_tasks.*": {"queue": "imports"},
        "app.tasks.cleanup_tasks.*": {"queue": "maintenance"},
    },

    # Default queue
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",

    # Define queues explicitly
    task_queues=(
        Queue(
            "default",
            Exchange("default"),
            routing_key="default",
            queue_arguments={"x-max-priority": 10},
        ),
        Queue(
            "imports",
            Exchange("imports"),
            routing_key="imports",
            queue_arguments={"x-max-priority": 10},
        ),
        Queue(
            "maintenance",
            Exchange("maintenance"),
            routing_key="maintenance",
            queue_arguments={"x-max-priority": 5},
        ),
    ),

    # Beat schedule (periodic tasks)
    beat_schedule={
        "cleanup-old-files-daily": {
            "task": "app.tasks.cleanup_tasks.cleanup_old_files",
            "schedule": crontab(hour=2, minute=0),  # Run at 2 AM daily
            "options": {"queue": "maintenance"},
        },
        "cleanup-old-import-jobs-weekly": {
            "task": "app.tasks.cleanup_tasks.cleanup_old_import_jobs",
            "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday at 3 AM
            "options": {"queue": "maintenance"},
        },
    },
)

# Task retry policy with exponential backoff
celery_app.conf.task_annotations = {
    "*": {
        "rate_limit": "100/m",  # Maximum 100 tasks per minute
        "retry_backoff": True,  # Enable exponential backoff
        "retry_backoff_max": 600,  # Maximum 10 minutes between retries
        "retry_jitter": True,  # Add random jitter to prevent thundering herd
    },
    "app.tasks.import_tasks.process_import": {
        "rate_limit": "10/m",  # Limit import tasks to 10 per minute
        "max_retries": 3,
        "soft_time_limit": 1800,  # 30 minutes
        "time_limit": 2400,  # 40 minutes
    },
}


# Task base class with default retry configuration
class RetryTask(celery_app.Task):
    """Base task with automatic retry on failure"""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True


# Health check task
@celery_app.task(name="app.tasks.health_check")
def health_check():
    """Simple health check task for monitoring"""
    return {"status": "healthy", "message": "Celery is running"}


# Optional: Configure Celery for development vs production
if ENVIRONMENT == "development":
    celery_app.conf.update(
        task_always_eager=False,  # Don't run tasks synchronously in dev
        task_eager_propagates=True,  # Propagate exceptions in eager mode
    )
elif ENVIRONMENT == "production":
    celery_app.conf.update(
        task_always_eager=False,
        worker_pool="prefork",  # Use prefork pool in production
        worker_concurrency=4,  # Number of worker processes
    )
