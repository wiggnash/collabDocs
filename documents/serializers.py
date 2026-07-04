from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from documents.models import Document
from users.models import User


class DocumentSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "content",
            "status",
            "workspace",
            "created_by",
            "tags",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=Document.objects.all(),
                fields=["workspace", "title"],
                message="A document with this title already exists in this workspace.",
            )
        ]


class DocumentCreateSerializer(DocumentSerializer):
    """Create contract.

    Identical to the base: the client sends title/content/status/workspace/
    created_by. `saved_by` is intentionally NOT accepted — on create the
    creator saves version 1, so the view derives saved_by from created_by.
    """

    pass


class DocumentUpdateSerializer(DocumentSerializer):
    saved_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=True
    )

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ["saved_by"]
        read_only_fields = DocumentSerializer.Meta.read_only_fields + ["created_by"]

    def validate(self, attrs):
        if "saved_by" not in attrs:
            raise serializers.ValidationError(
                {"saved_by": "This field is required when updating a document."}
            )

        return attrs


class DocumentTagAttachSerializer(serializers.Serializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=False,
    )

    def validate_tags(self, value):
        normalized = []
        for name in value:
            cleaned = name.strip().lower()
            if not cleaned:
                raise serializers.ValidationError("Tag names cannot be blank.")
            if cleaned not in normalized:
                normalized.append(cleaned)
        return normalized
