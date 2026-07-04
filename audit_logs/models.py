import uuid
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        DELETED = "deleted", "Deleted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["actor", "timestamp"]),
            models.Index(fields=["model_name", "object_id"]),
        ]

    def __str__(self):
        return f"{self.action} {self.model_name}({self.object_id}) by {self.actor}"
