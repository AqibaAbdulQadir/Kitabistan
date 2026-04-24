from django.urls import path, re_path
from .views import GatewayView

urlpatterns = [
    re_path(r'^api/.*', GatewayView.as_view()),
]