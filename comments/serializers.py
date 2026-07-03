from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "document",
            "author",
            "content",
            "parent",
            "replies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data

    def validate(self, attrs):
        parent = attrs.get("parent")
        if parent and parent.document_id != attrs["document"].id:
            raise serializers.ValidationError(
                {"parent": "A reply's parent must belong to the same document."}
            )
        return attrs
