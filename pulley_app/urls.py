from django.urls import path
from . import views

urlpatterns = [
    path("", views.detect_pulleys, name="detect_pulleys"),
]