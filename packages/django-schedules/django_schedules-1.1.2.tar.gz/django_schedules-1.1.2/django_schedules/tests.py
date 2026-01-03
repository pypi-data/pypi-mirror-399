from django.test import TestCase


class TestUtils(TestCase):
    def test_schedule_spec(self):
        from .utils import ScheduleSpec

        self.assertCountEqual(ScheduleSpec().to_systemd_time(), ["*-*-* *:*:00"])
        self.assertCountEqual(
            ScheduleSpec.from_kwargs(
                mins=0,
            ).to_systemd_time(),
            ["*-*-* *:00:00"],
        )
        self.assertCountEqual(
            ScheduleSpec.from_kwargs(
                hour=12,
                mins=0,
            ).to_systemd_time(),
            ["*-*-* 12:00:00"],
        )
        self.assertCountEqual(
            ScheduleSpec.from_kwargs(
                hour=23,
                mins=12,
                month=1,
            ).to_systemd_time(),
            ["*-01-* 23:12:00"],
        )
        self.assertCountEqual(
            ScheduleSpec.from_kwargs(
                hour=23,
                mins=12,
                month="feb",
            ).to_systemd_time(),
            ["*-02-* 23:12:00"],
        )
        self.assertCountEqual(
            ScheduleSpec.from_kwargs(
                hour=23,
                mins=12,
                month="dec",
                day_of_month=1,
            ).to_systemd_time(),
            ["*-12-01 23:12:00"],
        )
        self.assertCountEqual(
            ScheduleSpec.from_kwargs(
                hour=0,
                mins=0,
                day_of_week=0,
            ).to_systemd_time(),
            ["Sun *-*-* 00:00:00"],
        )
        self.assertCountEqual(
            ScheduleSpec.from_kwargs(
                hour=0,
                mins=0,
                day_of_week="mon",
            ).to_systemd_time(),
            ["Mon *-*-* 00:00:00"],
        )
        self.assertCountEqual(
            ScheduleSpec.from_kwargs(
                hour="0,12",
                mins=0,
                day_of_week="mon",
            ).to_systemd_time(),
            [
                "Mon *-*-* 00:00:00",
                "Mon *-*-* 12:00:00",
            ],
        )
        self.assertCountEqual(
            ScheduleSpec.from_kwargs(
                hour="0,12",
                mins=0,
                month="Jan,Apr,Jul,Oct",
                day_of_week="mon",
            ).to_systemd_time(),
            [
                "Mon *-01-* 00:00:00",
                "Mon *-01-* 12:00:00",
                "Mon *-04-* 00:00:00",
                "Mon *-04-* 12:00:00",
                "Mon *-07-* 00:00:00",
                "Mon *-07-* 12:00:00",
                "Mon *-10-* 00:00:00",
                "Mon *-10-* 12:00:00",
            ],
        )
        self.assertCountEqual(
            ScheduleSpec.from_kwargs(
                hour=0,
                mins=0,
                month=1,
                day_of_month=1,
                year="2022,2023",
            ).to_systemd_time(),
            [
                "2022-01-01 00:00:00",
                "2023-01-01 00:00:00",
            ],
        )
