import uuid
from django.db import models


class DocumentVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        "documents.Document",
        on_delete=models.CASCADE,
        related_name="versions",
    )
    content = models.TextField(blank=True)
    version_number = models.PositiveIntegerField()
    saved_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="saved_versions",
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["version_number"]

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"
