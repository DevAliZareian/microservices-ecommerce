import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_profile_created_on_user_create(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)

    def test_profile_str(self):
        self.assertEqual(str(self.user.profile), "testuser's profile")


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_success(self):
        response = self.client.post(
            '/api/v1/register/',
            data=json.dumps({
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'StrongPass123!',
                'password2': 'StrongPass123!',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        response = self.client.post(
            '/api/v1/register/',
            data=json.dumps({
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'StrongPass123!',
                'password2': 'DifferentPass456!',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_username(self):
        User.objects.create_user(
            username='existing', email='ex@example.com', password='pass123'
        )
        response = self.client.post(
            '/api/v1/register/',
            data=json.dumps({
                'username': 'existing',
                'email': 'new@example.com',
                'password': 'StrongPass123!',
                'password2': 'StrongPass123!',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 409)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_login(self.user)

    def test_get_profile(self):
        response = self.client.get('/api/v1/profile/')
        self.assertEqual(response.status_code, 200)

    def test_patch_profile(self):
        response = self.client.patch(
            '/api/v1/profile/',
            data=json.dumps({'phone_number': '+1234567890'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.phone_number, '+1234567890')

    def test_get_profile_unauthenticated(self):
        self.client.logout()
        response = self.client.get('/api/v1/profile/')
        self.assertIn(response.status_code, [401, 403])


class SelectorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='seluser',
            email='sel@example.com',
            password='testpass123',
        )

    def test_get_user_by_id(self):
        from accounts.selectors.user_selector import get_user_by_id
        result = get_user_by_id(self.user.id)
        self.assertEqual(result.username, 'seluser')

    def test_get_user_by_username(self):
        from accounts.selectors.user_selector import get_user_by_username
        result = get_user_by_username('seluser')
        self.assertEqual(result.email, 'sel@example.com')

    def test_get_user_not_found(self):
        from accounts.selectors.user_selector import get_user_by_id
        from shared.common.exceptions import NotFoundError
        with self.assertRaises(NotFoundError):
            get_user_by_id(99999)
