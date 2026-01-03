# Django Schedules

This app allows you to define routines that should run periodically (e.g. every day at 0:00, ...).
They will be triggered by systemd-timers or cron.

## Define Routines

1. Add "schedules" to your `INSTALLED_APPS` setting.
2. Add a file called `schedules.py` to your django app.
3. Define functions in this file.
4. Each function which is a timer job should be decorated by the `register` decorater:

### Example:

```py
import django_schedules

@django_schedules.register(mins=0, hour=0)
def run_at_midnight(**kwargs):
    print('hello')

@django_schedules.register(mins=3, hour=18, day_of_month=2, month='5,11', lock=False, job_name='foobar')
def bar(**kwargs):
    """
    Run on 2.5. and 2.11. at 18:03.
    Don't use locking (allow to run this job more than once at the same time).
    The job will be called 'foobar'.'
    """
    print('hello')

```

## Commands

Now you can use following management commands:

```sh
./manage.py schedules_list  # list all available jobs
./manage.py schedules_update_systemd [-u user] [--out-path path]  # generate systemd units (for user 'user' (default root))
./manage.py schedules_update_cron [-u user] [-o file]  # generate crontab "code" (for user 'user' (default root)) (and write it to file file)
./manage.py schedules_run [<app_name>:]<job_name> [additional_args, ...]  # run the job app_name:job_name
```

## Installation

- Write your code (see above)
- Run `./manage.py schedules_list` to verify all jobs are registered as expected
- Run `./manage.py schedules_update_systemd -u $DJANGO_USER [--out-path /etc/systemd/system/]` to generate systemd units
- Or run `./manage.py schedules_update_cron -u $DJANGO_USER -o /etc/cron.d/$DJANGO_PROJECT_NAME` to let the jobs run by system cron
