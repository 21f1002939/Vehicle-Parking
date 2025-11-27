"""
Celery Beat Scheduler Runner for Windows
"""
import sys
from celery_app import celery

if __name__ == '__main__':
    # Start the beat scheduler
    celery.start(argv=['beat', '--loglevel=info'])
