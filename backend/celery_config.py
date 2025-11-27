from celery import Celery
from celery.schedules import crontab

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get('broker_url') or app.config.get('CELERY_BROKER_URL'),
        backend=app.config.get('result_backend') or app.config.get('CELERY_RESULT_BACKEND')
    )
    
    celery.conf.update(app.config)
    
    celery.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'tasks.send_daily_reminder',
            'schedule': crontab(minute='*'),
        },
        'generate-monthly-reports': {
            'task': 'tasks.generate_monthly_report',
            'schedule': crontab(minute='*'),
        },
    }
    
    celery.conf.timezone = 'UTC'
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
