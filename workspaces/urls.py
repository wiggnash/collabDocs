from rest_framework.routers import DefaultRouter

# from .views import WorkspaceViewSet  # T03: import once the viewset exists

router = DefaultRouter()
# router.register(r"workspaces", WorkspaceViewSet, basename="workspace")  # T03

urlpatterns = router.urls
