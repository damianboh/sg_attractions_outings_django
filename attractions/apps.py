from django.apps import AppConfig


class AttractionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attractions'

    def ready(self):
        import attractions.signals
