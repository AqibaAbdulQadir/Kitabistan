from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer, GoogleLoginSerializer
from .adapter import CustomGoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialToken, SocialApp
from allauth.socialaccount.helpers import complete_social_login


class GoogleLoginView(SocialLoginView):
    adapter_class = CustomGoogleOAuth2Adapter
    serializer_class = GoogleLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data['access_token']
        app = SocialApp.objects.get(provider='google')
        token = SocialToken(app=app, token=access_token)
        
        adapter = self.adapter_class(request)
        login = adapter.complete_login(request, app, token, response={})

        # Login with backend specified
        from django.contrib.auth import login as django_login
        login.user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
        django_login(request, login.user, backend='allauth.account.auth_backends.AuthenticationBackend')

        refresh = RefreshToken.for_user(login.user)

        return Response({
            'user': {
                'id': login.user.id,
                'email': login.user.email,
                'name': login.user.name,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

class AuthViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'register':
            return RegisterSerializer
        elif self.action == 'login':
            return LoginSerializer
        elif self.action == 'profile':
            return ProfileSerializer
        return RegisterSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully',
            'user': {'id': user.id, 'email': user.email, 'name': user.name},
            'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)},
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'user': {'id': user.id, 'email': user.email, 'name': user.name},
            'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)},
        })

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        if request.method == 'PUT':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        return Response({'service': 'user-service', 'status': 'healthy'})