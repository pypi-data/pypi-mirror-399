"""Utils used by django schedules."""

import importlib
import re
import sys
import typing
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from warnings import warn

from django.apps import apps

from .conf import settings

if typing.TYPE_CHECKING:
    from .schedules import RegisteredJobs


class TimeSpecsSubDataStructure(typing.TypedDict):
    min: int
    max: int
    extra: set[str]


class TimeSpecsDataStructure(typing.TypedDict):
    mins: TimeSpecsSubDataStructure
    hour: TimeSpecsSubDataStructure
    day_of_month: TimeSpecsSubDataStructure
    month: TimeSpecsSubDataStructure
    day_of_week: TimeSpecsSubDataStructure
    year: TimeSpecsSubDataStructure


MONTH_3 = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]
WEEKDAYS_3 = [
    "sun",
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
]

TIME_SPECS: TimeSpecsDataStructure = {
    "mins": {"min": 0, "max": 59, "extra": set[str]()},
    "hour": {"min": 0, "max": 23, "extra": set[str]()},
    "day_of_month": {"min": 1, "max": 31, "extra": set[str]()},
    "month": {
        "min": 1,
        "max": 12,
        "extra": set(MONTH_3),
    },
    "day_of_week": {
        "min": 0,
        "max": 7,
        "extra": set(WEEKDAYS_3),
    },
    "year": {
        "min": 0,
        "max": 9999,
        "extra": set[str](),
    },
}


@dataclass
class ScheduleSpec:
    """Schedule specification for a timer job."""

    # TODO support things like */2, 1-5 and 1..5
    mins: list[int | str] = field(default_factory=lambda: ["*"])
    hour: list[int | str] = field(default_factory=lambda: ["*"])
    day_of_month: list[int | str] = field(default_factory=lambda: ["*"])
    month: list[int | str] = field(default_factory=lambda: ["*"])
    day_of_week: list[int | str] = field(default_factory=lambda: ["*"])
    year: list[int | str] = field(default_factory=lambda: ["*"])

    def to_cron_spec(self) -> str:
        if self.year != ["*"]:
            raise ValueError("Year is not supported for cron")
        mins_str = ",".join(map(str, self.mins))
        hour_str = ",".join(map(str, self.hour))
        day_of_month_str = ",".join(map(str, self.day_of_month))
        month_str = ",".join(map(str, self.month))
        day_of_week_str = ",".join(map(str, self.day_of_week))
        return f"{mins_str} {hour_str} {day_of_month_str} {month_str} {day_of_week_str}"

    def to_systemd_time(self) -> Iterable[str]:
        def craft_systemd_time(
            mins: str | int = "*",
            hour: str | int = "*",
            day_of_month: str | int = "*",
            month: str | int = "*",
            day_of_week: str | int = "*",
            year: str | int = "*",
        ) -> str:
            if str(month).lower() in MONTH_3:
                month = MONTH_3.index(str(month).lower()) + 1

            # format
            def format_digits(value: str | int, num_digits=2) -> str:
                if value == "*":
                    return str(value)
                else:
                    return f"{int(value):0{num_digits}}"

            month = format_digits(month)
            day_of_month = format_digits(day_of_month)
            hour = format_digits(hour)
            mins = format_digits(mins)
            year = format_digits(year)

            # craft string
            ret = f"{year}-{month}-{day_of_month} {hour}:{mins}:00"
            if day_of_week != "*":
                if day_of_week not in WEEKDAYS_3:
                    day_of_week = WEEKDAYS_3[int(day_of_week)]
                day_of_week = day_of_week.title()
                ret = f"{day_of_week} {ret}"

            return ret

        for single_mins in self.mins:
            for single_hour in self.hour:
                for single_day_of_month in self.day_of_month:
                    for single_month in self.month:
                        for single_day_of_week in self.day_of_week:
                            for single_year in self.year:
                                yield craft_systemd_time(
                                    mins=single_mins,
                                    hour=single_hour,
                                    day_of_month=single_day_of_month,
                                    month=single_month,
                                    day_of_week=single_day_of_week,
                                    year=single_year,
                                )

    @classmethod
    def from_kwargs(
        cls,
        mins: int | str = "*",
        hour: int | str = "*",
        day_of_month: int | str = "*",
        month: int | str = "*",
        day_of_week: int | str = "*",
        year: int | str = "*",
    ) -> "ScheduleSpec":
        """
        Validate and return a list of TimeSpecs.

        :param mins: The minutes time specification for this timer job.
        :param hour: The hour time specification for this timer job.
        :param day_of_month: The day_of_month time specification for this timer job.
        :param month: The month time specification for this timer job.
        :param day_of_week: The day_of_week time specification for this timer job.
        :param year: The year time specification for this timer job.
        """

        if all((t == "*" for t in locals())):
            warn(
                "Your schedule specification is * * * * *. Do you really want to run this every minute?"
                " Hint: Use */1 to avoid this message"
            )

        # sanity check
        _warning_message = (
            "{} is specified but all others are *. "
            + "This will cause running the job very often on a day."
        )

        if day_of_week != "*" and mins == "*":
            warn(_warning_message.format("day_of_week"))
        elif day_of_month != "*" and mins == "*":
            warn(_warning_message.format("day_of_month"))
        elif month != "*" and mins == "*" and hour == "*":
            warn(_warning_message.format("month"))

        def _validate_schedule(
            value: str | int | list[str | int], time_type: str
        ) -> typing.Iterable[str | int]:
            """Return the cleaned value(s) if it is a valid cron schedule spec."""
            assert time_type in TIME_SPECS.keys()

            min_val: int = TIME_SPECS[time_type]["min"]
            max_val: int = TIME_SPECS[time_type]["max"]

            values: typing.Iterable[str | int]
            nth_match = re.match(r"^\*/(?P<dist>\d+)$", str(value))

            if value == "*":
                yield str(value)
                return
            elif nth_match:
                dist = int(nth_match.group("dist"))

                if not max(1, min_val) <= dist <= max_val:
                    raise ValueError(f"Invalid time distance spec '{dist}' in '{value}'")

                yield str(value)
                return
            elif isinstance(value, str):
                values = value.split(",")
            elif isinstance(value, list):
                values = value
            elif isinstance(value, int):
                values = [value]
            else:
                raise ValueError(f"Value {value} for {type(value)} has invalid type {time_type}")

            for val in values:
                if str(val).lower() in TIME_SPECS[time_type]["extra"]:
                    yield val
                    continue

                try:
                    int_val = int(val)
                except ValueError as err:
                    raise ValueError(f"Invalid {time_type} time spec '{val}'") from err

                if not min_val <= int_val <= max_val:
                    raise ValueError(
                        f"The time value {int_val} is invalid. "
                        f"It has to be between {min_val} and {max_val}."
                    )

                yield int_val

        mins_list = list(_validate_schedule(mins, "mins"))
        hour_list = list(_validate_schedule(hour, "hour"))
        day_of_month_list = list(_validate_schedule(day_of_month, "day_of_month"))
        month_list = list(_validate_schedule(month, "month"))
        day_of_week_list = list(_validate_schedule(day_of_week, "day_of_week"))
        year_list = list(_validate_schedule(year, "year"))
        return cls(
            mins=mins_list,
            hour=hour_list,
            day_of_month=day_of_month_list,
            month=month_list,
            day_of_week=day_of_week_list,
            year=year_list,
        )

    def __str__(self) -> str:
        return self.to_cron_spec()


def register_all_jobs() -> dict[str, "RegisteredJobs"]:
    """Import all apps from ``INSTALLED_APPS``. Required to register all jobs."""
    schedules_modules = (
        *settings.DJANGO_SCHEDULES_EXTRA_MODULES,
        *(f"{app.module.__name__}.schedules" for app in apps.get_app_configs() if app.module),
    )

    for module in schedules_modules:
        try:
            # @register decorators will be executed by importing the module.
            importlib.import_module(module)
        except ModuleNotFoundError as err:
            if not err.name == module:
                print(
                    f"Detected ModuleNotFoundError during import of {module}:",
                    file=sys.stderr,
                )
                print(err, file=sys.stderr)

    # the @register decorators register their app into REGISTERED_JOBS
    from .schedules import REGISTERED_JOBS

    return REGISTERED_JOBS


def split_schedule_spec_and_kwargs(
    register_args: dict[str, typing.Any],
) -> tuple[dict[str, typing.Any], dict[str, typing.Any]]:
    """
    Split ``schedule_spec`` args and ``kwargs`` for the schedules job in kwargs given to register decorator.

    :param register_args: The arguments given to the :func:`~django_schedules.schedules.register`.
    """
    schedule_specs = dict[str, typing.Any]()
    kwargs = dict[str, typing.Any]()

    for key, value in register_args.items():
        if key in TIME_SPECS.keys():
            schedule_specs[key] = value
        else:
            kwargs[key] = value

    return (schedule_specs, kwargs)


def get_job_run_command(job_name: str) -> str:
    """Return the full command to run `job_name`."""
    manage_py_file_name = Path(sys.argv[0]).absolute()
    return f"{sys.executable} {manage_py_file_name} schedules_run {job_name}"
