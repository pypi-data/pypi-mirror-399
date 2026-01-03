"""Register timer jobs using @register decorator."""

import typing
from dataclasses import dataclass

from .utils import ScheduleSpec, split_schedule_spec_and_kwargs


@dataclass
class RegisteredJobs:
    """Data structure for a registered job."""

    #: python function to run
    func: typing.Callable
    #: lock agains concurrent execution
    lock: bool
    #: description of the job
    desc: str
    #: the schedule specification when this job should run
    time: ScheduleSpec
    #: fix arguments for the job function
    args: dict[str, typing.Any]


#: The dict that will be used to collect all registered timer jobs.
REGISTERED_JOBS = dict[str, RegisteredJobs]()


def register(lock: bool = True, job_name: str | None = None, **kwargs):
    """
    Decorator to register functions as timer job.

    :param job_name: The name for this job. If empty -> the func name will be used. Add a job_name to register one func more than once
    :param mins: [0-59], run every `mins` minute, default '*'
    :param hour: [0-23], run every `hour` hour, default '*'
    :param day_of_month: [1-31], run every `day_of_month` day of month, default '*'
    :param month: [1-12], run every `month` month, default '*'
    :param day_of_week: [0-6], run every `day_of_week` day of week, default '*'
    :param lock: Let run func only once at the same time.

    All other kwargs will be passed to function.

    More about cron time specifications: https://en.wikipedia.org/wiki/Cron
    The values can be int or str.

    Examples:
    ---------
        .. code-block:: py

            @django_schedules.register(mins=0, lock=False)
            def job1(**kwargs):
                '''
                This func can run more than once at the same time. (lock=False)
                It start's everytime when mins=0 -> every hour
                '''
                print(job1.__doc__)

            @django_schedules.register(mins=3, hour=18, day_of_month=2, month='5,11')
            def job2(**kwargs):
                '''
                This func can only run once at the same time. (lock=True)
                It runs on 2.5. and on 2.11. at 18:03.
                '''
                print(job2.__doc__)
    """

    def _inner_register(func: typing.Callable, lock: bool = lock) -> typing.Callable:
        """
        When decorator is called like: register(...).

        :param func: Function, that will be registered as timer job.
        :param lock: True to avoid running this function multiple times in parallel.
        """
        app_name = func.__module__.removesuffix(".schedules")
        default_job_name = "{app}:{func}".format(app=app_name, func=func.__name__)

        schedule_specs, args = split_schedule_spec_and_kwargs(kwargs)

        # desc is the first line of the docstring of the function if exists
        REGISTERED_JOBS[job_name if job_name else default_job_name] = RegisteredJobs(
            func=func,
            lock=lock,
            desc=func.__doc__.strip().splitlines()[0] if func.__doc__ else "",
            time=ScheduleSpec.from_kwargs(**schedule_specs),
            args=args,
        )

        return func

    return _inner_register
