from django.db import transaction
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db.models import Q

from document_versions.models import DocumentVersion
from document_versions.serializers import DocumentVersionSerializer

from .models import Document
from .serializers import (
    DocumentCreateSerializer,
    DocumentSerializer,
    DocumentUpdateSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_queryset(self):
        qs = Document.objects.select_related("workspace", "created_by")
        params = self.request.query_params

        document_status = params.get("status")
        if document_status:
            qs = qs.filter(status=document_status)

        workspace = params.get("workspace")
        if workspace:
            qs = qs.filter(workspace_id=workspace)

        search = params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))

        return qs

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

    @action(detail=True, methods=["get"], url_path="versions")
    def document_versions(self, request, pk=None):
        document = self.get_object()
        versions = document.versions.order_by("-version_number")
        serializer = DocumentVersionSerializer(versions, many=True)

        return Response(serializer.data)
