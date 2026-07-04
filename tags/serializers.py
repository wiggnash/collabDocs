from rest_framework import serializers

from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)

    class Meta:
        model = Tag
        fields = ["id", "name", "documents", "created_at"]
        read_only_fields = ["id", "documents", "created_at"]

    def validate_name(self, value):
        normalized = value.strip().lower()
        if not normalized:
            raise serializers.ValidationError("Tag name cannot be blank.")

        qs = Tag.objects.filter(name=normalized)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A tag with this name already exists.")

        return normalized
