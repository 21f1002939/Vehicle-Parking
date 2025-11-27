"""
Celery application entry point
This file makes celery discoverable for the celery worker command
"""
from app import celery, app
import tasks  # Import tasks module to register all tasks

# This allows running: celery -A celery_app worker
__all__ = ['celery', 'app']
