"""
Celery Worker Runner for Windows
"""
import sys
from celery_app import celery, app
import tasks  # Import tasks module to register all tasks with Celery

if __name__ == '__main__':
    # Start the worker with solo pool (required for Windows)
    celery.worker_main(argv=['worker', '--loglevel=info', '--pool=solo'])
