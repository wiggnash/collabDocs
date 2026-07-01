from rest_framework import serializers

from workspaces.models import Workspace

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "is_active",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]

class WorkspaceDetailSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Workspace
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "member_count",
            "is_active",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]
