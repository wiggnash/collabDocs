from rest_framework.routers import DefaultRouter

# from .views import UserViewSet  # T03: import once the viewset exists

router = DefaultRouter()
# router.register(r"users", UserViewSet, basename="user")  # T03

urlpatterns = router.urls
