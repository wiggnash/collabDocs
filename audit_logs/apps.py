from django.apps import AppConfig


class AuditLogsConfig(AppConfig):
    name = 'audit_logs'

    def ready(self):
        from . import signals  # noqa: F401
