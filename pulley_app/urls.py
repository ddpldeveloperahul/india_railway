from django.urls import path,include
from .views import DatasetViewSet
from . import views
from rest_framework.routers import DefaultRouter




router = DefaultRouter()
router.register(r'datasets', DatasetViewSet)
urlpatterns = [
    path("", views.detect_pulleys, name="detect_pulleys"),
    path('', include(router.urls)),
]