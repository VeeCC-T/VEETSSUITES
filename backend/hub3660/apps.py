"""
HUB3660 app configuration.
"""

from django.apps import AppConfig


class Hub3660Config(AppConfig):
    """Configuration for the HUB3660 course management app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hub3660'
    verbose_name = 'HUB3660 Course Management'