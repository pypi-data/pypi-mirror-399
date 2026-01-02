"""
Django app configuration for django_context_memory

This allows the library to be used as a Django app, providing a web interface
in addition to CLI and Python API functionality.
"""

from django.apps import AppConfig


class DjangoContextMemoryConfig(AppConfig):
    """Django app configuration for context memory"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_context_memory'
    verbose_name = 'Django Context Memory'

    def ready(self):
        """
        App initialization

        This method is called when Django starts up.
        We can use it for any initialization tasks.
        """
        import logging
        from . import __version__

        logger = logging.getLogger(__name__)
        logger.info(f"Django Context Memory v{__version__} loaded")
