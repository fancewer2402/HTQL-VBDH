from django.apps import AppConfig


class QlvbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'QLVB'

    def ready(self):
        import QLVB.signals