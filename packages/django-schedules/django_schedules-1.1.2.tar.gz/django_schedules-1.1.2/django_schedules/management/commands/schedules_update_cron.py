"""Update system's crontab."""

import getpass
import os
import sys
from argparse import FileType

from django.conf import ENVIRONMENT_VARIABLE as DJ_SETTINGS_ENV_VAR
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from ...conf import settings
from ...utils import get_job_run_command, register_all_jobs


class Command(BaseCommand):
    """Update system crontab."""

    help = __doc__ or ""
    #: This line will be added on top of the generated crontab file.
    GENERATED_CRONTAB_HEADER = "### generated jobs by django schedules ###"

    def add_arguments(self, parser):
        """Add arguments to the argument parser."""
        parser.add_argument(
            "-u",
            "--user",
            default=getpass.getuser(),
            type=str,
            help=_("Run cronjobs as this user"),
        )
        parser.add_argument(
            "-o",
            "--out",
            default=sys.stdout,
            type=FileType("w"),
            help=_("Write to this file instead of stdout"),
        )
        parser.add_argument(
            "--path",
            default=os.environ.get("PATH"),
            type=str,
            help=_("The PATH to use."),
        )

    def handle(self, *args, **options):
        """Run the command."""
        registered_jobs = register_all_jobs()

        print(Command.GENERATED_CRONTAB_HEADER, file=options["out"])
        print(f"MAIL={settings.DJANGO_SCHEDULES_MAIL}", file=options["out"])
        print(f"PATH={options['path']}", file=options["out"])
        if settings.SETTINGS_MODULE:
            print(
                f"{DJ_SETTINGS_ENV_VAR}={settings.SETTINGS_MODULE}",
                file=options["out"],
            )

        for job_name, job in registered_jobs.items():
            print("", file=options["out"])
            print(f"# {job.desc}", file=options["out"])
            invoke_cmd = get_job_run_command(job_name)
            print(
                f"{job.time.to_cron_spec()} {options['user']} {invoke_cmd}",
                file=options["out"],
            )

            if options["out"].name != "<stdout>":
                self.stdout.write(self.style.SUCCESS(_(f"{options['out'].name} written")))
