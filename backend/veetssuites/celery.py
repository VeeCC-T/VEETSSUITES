"""
Celery configuration for VeetsSuites project.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veetssuites.settings')

app = Celery('veetssuites')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure task routes for different queues
app.conf.task_routes = {
    'veetssuites.tasks.warm_cache_task': {'queue': 'cache'},
    'veetssuites.tasks.process_cv_upload': {'queue': 'file_processing'},
    'veetssuites.tasks.send_notification_email': {'queue': 'notifications'},
    'veetssuites.tasks.process_exam_results': {'queue': 'analytics'},
    'veetssuites.tasks.process_zoom_recording': {'queue': 'file_processing'},
    'veetssuites.tasks.cleanup_expired_tokens': {'queue': 'maintenance'},
    'veetssuites.tasks.generate_analytics_report': {'queue': 'analytics'},
    'veetssuites.tasks.batch_process_mcq_import': {'queue': 'file_processing'},
    'veetssuites.tasks.optimize_database_task': {'queue': 'maintenance'},
}

# Configure task priorities
app.conf.task_default_priority = 5
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
app.conf.worker_disable_rate_limits = False

# Configure result backend settings
app.conf.result_expires = 3600  # Results expire after 1 hour
app.conf.result_persistent = True

# Configure retry settings
app.conf.task_default_retry_delay = 60  # 1 minute
app.conf.task_max_retries = 3

# Configure monitoring
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')
    return 'Debug task completed'