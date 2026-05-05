from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialLogin, SocialAccount
from django.contrib.auth import get_user_model
import jwt
import json

User = get_user_model()

class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    def complete_login(self, request, app, token, **kwargs):
        id_token = token.token
        decoded = jwt.decode(id_token, options={"verify_signature": False})
        
        print("=" * 50, flush=True)
        print("GOOGLE USER DATA:", flush=True)
        print(json.dumps(decoded, indent=2, default=str), flush=True)
        print("=" * 50, flush=True)
        
        email = decoded.get('email', '')
        name = decoded.get('name', '')
        sub = decoded.get('sub', email)
        
        # Create or get user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'name': name or email.split('@')[0],
                'username': email.split('@')[0]
            }
        )
        
        # Verify email
        EmailAddress.objects.get_or_create(
            user=user,
            email=email,
            defaults={'verified': True, 'primary': True}
        )
        
        # Create or get social account
        social_account, _ = SocialAccount.objects.get_or_create(
            user=user,
            provider='google',
            defaults={'uid': sub}
        )
        
        # Return login WITHOUT calling complete_social_login
        login = SocialLogin(user=user)
        login.account = social_account
        login.token = token
        
        return login