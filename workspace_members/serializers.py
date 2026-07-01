from rest_framework import serializers

from users.serializers import UserSerializer

from .models import WorkspaceMember


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    """Read serializer: nested user detail + role."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = [
            "id",
            "workspace",
            "user",
            "role",
            "joined_at",
            "updated_at",
        ]
        read_only_fields = fields


class WorkspaceMemberCreateSerializer(serializers.ModelSerializer):
    """Write serializer: accept a user id + role for POST .../members/."""

    class Meta:
        model = WorkspaceMember
        fields = ["id", "user", "role"]
        read_only_fields = ["id"]
