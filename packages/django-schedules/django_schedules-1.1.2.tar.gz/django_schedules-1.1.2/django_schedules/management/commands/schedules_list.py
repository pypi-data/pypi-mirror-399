"""List all registered timer jobs."""

from django.core.management.base import BaseCommand
from tabulate import tabulate

from ...utils import register_all_jobs


class Command(BaseCommand):
    """List all registered timer jobs."""

    help = __doc__ or ""

    def handle(self, *args, **options):
        """Run the command."""
        registered_jobs = register_all_jobs()

        header_names = map(
            self.style.MIGRATE_HEADING,
            ["name", "locks", "description", "schedule", "args"],
        )
        job_list = sorted(
            [
                self.style.MIGRATE_LABEL(name),
                self.style.SUCCESS("yes") if job.lock else self.style.WARNING("no"),
                job.desc,
                ", ".join(job.time.to_systemd_time())
                if job.time
                else self.style.WARNING("manually"),
                ", ".join(("{0}: {1}".format(k, v) for k, v in job.args.items())),
            ]
            for name, job in registered_jobs.items()
        )
        print(
            tabulate(
                job_list,
                headers=tuple(header_names),
            )
        )
