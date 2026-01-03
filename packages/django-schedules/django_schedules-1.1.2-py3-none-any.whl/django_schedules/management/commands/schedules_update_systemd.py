"""Update systemd timers."""

import getpass
from pathlib import Path

from django.conf import ENVIRONMENT_VARIABLE as DJ_SETTINGS_ENV_VAR
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from ...conf import settings
from ...utils import (
    get_job_run_command,
    register_all_jobs,
)


class Command(BaseCommand):
    """Update systemd timers."""

    help = __doc__ or ""
    #: This line will be added on top of the generated systemd unit and timer files.
    GENERATED_COMMENT = "generated jobs by django schedules"

    def add_arguments(self, parser):
        """Add arguments to the argument parser."""
        parser.add_argument(
            "-u",
            "--user",
            default=getpass.getuser(),
            type=str,
            help=_("Run timer job as this user"),
        )
        parser.add_argument(
            "--out-path",
            default="/etc/systemd/system/",
            type=Path,
            help=_("Generate systemd units into this path"),
        )

    def handle(self, *args, **options):
        """Run the command."""
        registered_jobs = register_all_jobs()

        project_name = settings.SETTINGS_MODULE.split(".", 1)[0]
        working_directory = Path().absolute()
        environment = ""
        if settings.SETTINGS_MODULE:
            environment = f"Environment={DJ_SETTINGS_ENV_VAR}={settings.SETTINGS_MODULE}"

        for job_name, job in registered_jobs.items():
            job_name_short = job_name.split(":", 1)[1]
            unit_name = f"{project_name}-{job_name_short}".replace("_", "-")
            service_file_path = options["out_path"] / f"{unit_name}.service"
            timer_file_path = options["out_path"] / f"{unit_name}.timer"
            invoke_cmd = get_job_run_command(job_name)

            schedule_spec = "\n".join(f"OnCalendar={spec}" for spec in job.time.to_systemd_time())

            with timer_file_path.open("w") as timer_file:
                print(
                    f"""
# {self.GENERATED_COMMENT}

[Unit]
Description={job.desc or _("Run django schedules job")}

[Timer]
{schedule_spec}
Unit={unit_name}.service

[Install]
WantedBy=timers.target
""".strip(),
                    file=timer_file,
                )

            self.stdout.write(self.style.SUCCESS(_(f"{timer_file_path} written")))

            with service_file_path.open("w") as service_file:
                print(
                    f"""
# {self.GENERATED_COMMENT}

[Unit]
Description={job.desc or _("Run django schedules job")}

[Service]
Type=oneshot
User={options["user"]}
ExecStart={invoke_cmd}
WorkingDirectory={working_directory}
{environment}
""".strip(),
                    file=service_file,
                )
            self.stdout.write(self.style.SUCCESS(_(f"{service_file_path} written")))
