"""Run a timer job or list them."""

import atexit
import logging
import os
import sys
import tempfile
import typing
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from ...utils import register_all_jobs

if typing.TYPE_CHECKING:
    from ...schedules import RegisteredJobs


class Command(BaseCommand):
    """Run a timer job."""

    help = __doc__ or ""
    logger = logging.getLogger("schedules")
    registered_jobs = register_all_jobs()

    def add_arguments(self, parser):
        """Add arguments to the argument parser."""
        job_names = list(Command.registered_jobs.keys())
        job_names += [n.split(":")[-1] for n in Command.registered_jobs.keys()]

        parser.add_argument("job_name", type=str, choices=job_names or None)
        parser.add_argument("job_args", nargs="*")  # args for job

    @staticmethod
    def _get_job_by_name(job_name: str) -> tuple[str, "RegisteredJobs"]:
        """
        Return the long name and the registered job entry for job job_name.

        The name can be in the form '<app>:<job>' or '<job>'.
        Raises CommandError when:
            - job_name could not be found
            - the abbreviated form '<job>' is not unique
        """
        if ":" in job_name:
            try:
                return (job_name, Command.registered_jobs[job_name])
            except KeyError:
                raise CommandError(f"{job_name} could not be found")

        matches = {
            name: job for name, job in Command.registered_jobs.items() if name.endswith(job_name)
        }
        if not matches:
            raise CommandError(f"{job_name} could not be found")
        elif len(matches) > 1:
            raise CommandError(
                f'{job_name} is not an unique abbreviation. Use the long form "<app>:<job>".'
            )
        else:
            return matches.popitem()

    @staticmethod
    def _aquire_lock(job_name: str) -> None:
        """Aquire the lock for the job job_name. Exit if it already runs."""
        lock_file_name = Path(tempfile.gettempdir()) / f"django_schedules.{job_name}"

        try:
            lfd = os.open(lock_file_name, os.O_CREAT | os.O_EXCL)

            def remove_lock_file():
                """Remove the lock file on exit."""
                os.close(lfd)
                os.remove(lock_file_name)

            atexit.register(remove_lock_file)
        except FileExistsError:
            msg = (
                f"Job {job_name!r} is running already. "
                f"Remove the lockfile {lock_file_name!r} on errors."
            )
            Command.logger.error(msg)
            print(msg, file=sys.stderr)
            sys.exit(1)

    def handle(self, *_, **options):
        """Run the management command."""
        job_name, job = Command._get_job_by_name(options["job_name"])

        options.update(job.args)

        if job.lock:
            Command._aquire_lock(job_name)

        Command.logger.info("Started job %r", job_name)
        job.func(**options)
        Command.logger.info("Finished job %r", job_name)
