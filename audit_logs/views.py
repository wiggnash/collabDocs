from rest_framework import viewsets

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ModelViewSet):
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        qs = AuditLog.objects.select_related("actor")
        params = self.request.query_params

        actor = params.get("actor")
        if actor:
            qs = qs.filter(actor_id=actor)

        start = params.get("start")
        if start:
            qs = qs.filter(timestamp__gte=start)

        end = params.get("end")
        if end:
            qs = qs.filter(timestamp__lte=end)

        return qs
