"""
Celery Worker Runner
Run this script to start the Celery worker with beat scheduler for background jobs
"""

from app import app, celery
import tasks

if __name__ == '__main__':
    with app.app_context():
        celery.start()
