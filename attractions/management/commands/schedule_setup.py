from django.core.management.base import BaseCommand

from attractions.schedule_setup import schedule_setup

# run command directly for django celery beat schedule
class Command(BaseCommand):
    help = "Run the schedule_setup function"

    def handle(self, *args, **options):
        schedule_setup()
