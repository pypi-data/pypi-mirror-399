"""Register, manage and run timer jobs."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# so you can do `from django_schedules import register`
from .schedules import register  # NOQA


class DjangoSchedulesApp(AppConfig):
    """App configuration for django schedules."""

    name = "schedules"
    verbose_name = _("Django Schedules")


default_app_config = "django_schedules.DjangoSchedulesApp"
