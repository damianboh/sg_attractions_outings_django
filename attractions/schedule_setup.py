from django_celery_beat.models import IntervalSchedule, PeriodicTask
# run this to schedule email notifications

def schedule_setup():
    interval_schedule = IntervalSchedule.objects.create(
        every=1, period=IntervalSchedule.MINUTES
    )

    PeriodicTask.objects.create(
        task="attractions.tasks.notify_of_starting_soon", interval=interval_schedule
    )
