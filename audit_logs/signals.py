from django.db.models.signals import post_save
from django.dispatch import receiver

from documents.models import Document

from .models import AuditLog


@receiver(post_save, sender=Document)
def log_document_change(sender, instance, created, **kwargs):
    AuditLog.objects.create(
        actor=instance.created_by,
        action=AuditLog.Action.CREATED if created else AuditLog.Action.UPDATED,
        model_name="Document",
        object_id=str(instance.pk),
    )
