from django.db import transaction
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from document_versions.models import DocumentVersion

from .models import Document
from .serializers import (
    DocumentCreateSerializer,
    DocumentSerializer,
    DocumentUpdateSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    # use serializer based on create or update
    def get_serializer_class(self):
        if self.action == "create":
            return DocumentCreateSerializer
        if self.action in ("update", "partial_update"):
            return DocumentUpdateSerializer
        return DocumentSerializer

    def create(self, request, *args, **kwargs):
        # validate data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # save document and its version
        with transaction.atomic():
            document = serializer.save()

            DocumentVersion.objects.create(
                document=document,
                content=document.content,
                version_number=document.versions.count() + 1,
                saved_by=document.created_by,
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        document = self.get_object()

        # validate
        serializer = self.get_serializer(document, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # save and create document version
        with transaction.atomic():
            saved_by = serializer.validated_data.pop("saved_by")
            document = serializer.save()

            DocumentVersion.objects.create(
                document=document,
                content=document.content,
                version_number=document.versions.count() + 1,
                saved_by=saved_by,
            )

        return Response(serializer.data)
