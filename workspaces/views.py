from django.db import IntegrityError, transaction
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# model import
from .models import Workspace
from workspace_members.models import WorkspaceMember

# model serializer
from .serializers import WorkspaceDetailSerializer, WorkspaceSerializer
from workspace_members.serializers import (
    WorkspaceMemberCreateSerializer,
    WorkspaceMemberSerializer,
)

class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        return Workspace.objects.annotate(member_count=Count("memberships"))

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return WorkspaceDetailSerializer
        return WorkspaceSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            workspace = serializer.save()
            WorkspaceMember.objects.create(
                workspace=workspace,
                user=workspace.owner,
                role=WorkspaceMember.Role.ADMIN
            )

    @action(detail=True, methods=["get", "post"], url_path="members")
    def members(self, request, pk=None):
        workspace = self.get_object()

        if request.method == "POST":
            serializer = WorkspaceMemberCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            try:
                with transaction.atomic():
                    member = serializer.save(workspace=workspace)
            except IntegrityError:
                return Response(
                    {"detail": "This user is already a member of the workspace."},
                    status=status.HTTP_409_CONFLICT,
                )

            read_serializer = WorkspaceMemberSerializer(member)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)

        # GET: list members with their roles
        members = workspace.memberships.select_related("user")
        serializer = WorkspaceMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        workspace = self.get_object()

        summary = Workspace.objects.filter(pk=workspace.pk).aggregate(
            document_count=Count("documents", distinct=True),
            member_count=Count("memberships", distinct=True),
            comment_count=Count("documents__comments", distinct=True),
        )

        return Response(summary)
