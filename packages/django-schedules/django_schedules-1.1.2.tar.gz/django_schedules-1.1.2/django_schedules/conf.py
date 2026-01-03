"""Configurations for schedules."""

import typing

from appconf import AppConf
from django.conf import settings  # NOQA


class DjangoSchedulesAppConf(AppConf):
    """Add configurations to django config."""

    #: Configure cron to send mails to this address. Default is ``root``.
    MAIL: str = "root"

    #: List of extra timer job modules to load.
    EXTRA_MODULES: typing.List[str] = []
