from rest_framework import viewsets

from .models import Comment
from .serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("author", "document")
    serializer_class = CommentSerializer

    def get_queryset(self):
        qs = Comment.objects.select_related("author", "document")

        if self.action == "list":
            qs = qs.filter(parent__isnull=True)

            document = self.request.query_params.get("document")
            if document:
                qs = qs.filter(document_id=document)

        return qs
