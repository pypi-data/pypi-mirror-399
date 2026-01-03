from django.urls import path

from .views import Verify2FAView

urlpatterns = [
    path("verify/", Verify2FAView.as_view()),
]
