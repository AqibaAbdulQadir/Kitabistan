from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.profile_url = '/api/auth/profile/'
        
        # Create a test user
        self.test_user = User.objects.create_user(
            email='existing@test.com',
            name='Existing User',
            password='pass1234'
        )

    # ──────────────────────────────────────────────
    # REGISTRATION TESTS
    # ──────────────────────────────────────────────
    
    def test_register_success(self):
        """User can register with valid data"""
        response = self.client.post(self.register_url, {
            'email': 'new@test.com',
            'name': 'New User',
            'password': 'pass1234'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertEqual(response.data['user']['email'], 'new@test.com')

    def test_register_duplicate_email(self):
        """Cannot register with existing email"""
        response = self.client.post(self.register_url, {
            'email': 'existing@test.com',
            'name': 'Duplicate',
            'password': 'pass1234'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password(self):
        """Password must be at least 6 characters"""
        response = self.client.post(self.register_url, {
            'email': 'short@test.com',
            'name': 'Short Pass',
            'password': 'abc'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_email(self):
        """Email is required"""
        response = self.client.post(self.register_url, {
            'name': 'No Email',
            'password': 'pass1234'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ──────────────────────────────────────────────
    # LOGIN TESTS
    # ──────────────────────────────────────────────

    def test_login_success(self):
        """User can login with correct credentials"""
        response = self.client.post(self.login_url, {
            'email': 'existing@test.com',
            'password': 'pass1234'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], 'existing@test.com')

    def test_login_wrong_password(self):
        """Login fails with incorrect password"""
        response = self.client.post(self.login_url, {
            'email': 'existing@test.com',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Login fails for non-existent email"""
        response = self.client.post(self.login_url, {
            'email': 'ghost@test.com',
            'password': 'pass1234'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ──────────────────────────────────────────────
    # PROFILE TESTS
    # ──────────────────────────────────────────────

    def test_get_profile_authenticated(self):
        """Authenticated user can view their profile"""
        self.client.force_authenticate(user=self.test_user)
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'existing@test.com')
        self.assertEqual(response.data['name'], 'Existing User')

    def test_get_profile_unauthenticated(self):
        """Unauthenticated user cannot view profile"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        """User can update their name"""
        self.client.force_authenticate(user=self.test_user)
        response = self.client.put(self.profile_url, {
            'name': 'Updated Name'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')

    def test_cannot_update_email(self):
        """Email is read-only, cannot be changed"""
        self.client.force_authenticate(user=self.test_user)
        response = self.client.put(self.profile_url, {
            'email': 'hacked@test.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Email should remain unchanged
        self.assertEqual(response.data['email'], 'existing@test.com')

    # ──────────────────────────────────────────────
    # PASSWORD HASHING TEST
    # ──────────────────────────────────────────────

    def test_password_is_hashed(self):
        """Password stored in DB is hashed, not plaintext"""
        user = User.objects.get(email='existing@test.com')
        
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        self.assertNotEqual(user.password, 'pass1234')

class AdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='root',
            email='aqibaabdulqadir@gmail.com',
            password='aqiba123'
        )
        self.client.login(username='root', password='aqiba123')

    def test_admin_accessible(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_admin_users_list(self):
        response = self.client.get('/admin/accounts/user/')
        self.assertEqual(response.status_code, 200)

    def test_admin_add_user_page(self):
        response = self.client.get('/admin/accounts/user/add/')
        self.assertEqual(response.status_code, 200)