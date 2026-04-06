from django.apps import AppConfig


class AbotuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'about'
    verbose_name = 'sobre'

    def ready(self):
        import about.signals
