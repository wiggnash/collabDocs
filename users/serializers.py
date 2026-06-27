from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                lookup="iexact",
                message="user with this email already exists.",
            )
        ],
    )

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "is_active", "created_at", "updated_at"]

    def get_full_name(self, obj):
        return obj.full_name

    def validate_email(self, value):
        return value.strip().lower()

    def validate_phone(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise serializers.ValidationError(
                "Phone must be exactly 10 digits, with no spaces or special characters."
            )
        return value
