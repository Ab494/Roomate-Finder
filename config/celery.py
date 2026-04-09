# This file configures Celery for background task processing in the Roommate Finder app.
# Celery handles asynchronous tasks like match computation and notification sending.

import os
from celery import Celery

# Set Django settings module for Celery worker processes
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery application instance named 'roommate_finder'
app = Celery('roommate_finder')

# Load Celery configuration from Django settings
# Reads all CELERY_* prefixed settings from settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover and register tasks from all Django apps
# Looks for tasks.py files in each app directory
app.autodiscover_tasks()
