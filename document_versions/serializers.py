from rest_framework import fields, serializers
from .models import DocumentVersion

class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = [
            "id",
            "document",
            "content",
            "version_number",
            "saved_by",
            "saved_at",
        ]
        read_only_fields = fields
