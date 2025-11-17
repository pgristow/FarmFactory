"""
Celery Tasks Package

This package contains all async task definitions and the Celery application.
"""

from .celery_app import celery_app

__all__ = ["celery_app"]
