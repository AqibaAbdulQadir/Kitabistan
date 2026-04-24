from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, GoogleLoginView
from dj_rest_auth.views import (
    PasswordResetView, PasswordResetConfirmView,
    PasswordChangeView,
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
    
    # Password management
    path('auth/password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('auth/password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='password_change'),
    
    # Google login
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
]