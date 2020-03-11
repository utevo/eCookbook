from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')
ME_URL = reverse('users:me')


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTests(TestCase):
    """Test the public user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_succesful(self):
        """Test creating user with valid payload is successful"""

        payload = {
            'email': 'testemail@gmail.com',
            'password': 'test_password',
            'name': 'test_name',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_attempt_to_create_user_that_exists(self):
        """Test attempt of creating user with email that
        already exists is unsuccessful.
        """

        payload = {
            'email': 'testemail@gmail.com',
            'password': 'test_password',
            'name': 'test_name',
        }
        create_user(**payload)

        other_payload = {
            'email': payload['email'],
            'password': 'other_password',
            'name': 'other_name'
        }
        res = self.client.post(CREATE_USER_URL, other_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # check that user isn't changed
        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual(user.email, payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertEqual(user.name, payload['name'])

    def test_attempt_to_use_too_short_password(self):
        """Test creating user with too short password is unsuccessful."""

        payload = {
            'email': 'testemail@gmail.com',
            'password': 'short',
            'name': 'test_name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token(self):
        """Test creating token for user."""

        payload = {
            'email': 'testemail@gmail.com',
            'password': 'test_password',
            'name': 'test_name',
        }
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_attempt_to_create_token_using_invalid_password(self):
        """Test creating token using invalid credentials is unsuccessful."""

        payload = {
            'email': 'testemail@gmail.com',
            'password': 'test_password',
            'name': 'test_name',
        }
        create_user(**payload)

        other_payload = {
            'email': payload['email'],
            'password': 'bad_passowrd',
            'name': payload['name'],
        }
        res = self.client.post(TOKEN_URL, other_payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_attempt_to_create_token_using_invalid_email(self):
        """Test creating token using invalid email is unsuccessful."""

        payload = {
            'email': 'testemail@gmail.com',
            'password': 'test_password',
            'name': 'test_name',
        }
        create_user(**payload)

        other_payload = {
            'email': 'otheremail@gmail.com',
            'password': payload['password'],
            'name': payload['name'],
        }
        res = self.client.post(TOKEN_URL, other_payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_attempt_to_create_token_without_all_fields(self):
        """Test creating token with request that doesn't contain
        all requirements field is unsuccessful.
        """

        payload = {
            'email': 'testemail@gmail.com',
            'password': '',
            'name': 'test_name',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        payload = {
            'email': '',
            'password': 'test_password',
            'name': 'test_name',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_attempt_to_access_me_view_without_autorization(self):
        """Test accessing me view witout autorization is unsucessful."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test the private user API"""

    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='test_password',
            name='test_name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_read_profile_sucessful(self):
        """Test accessing to "me" view while being authenticated
        is successful.
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_on_me_view_not_allowed(self):
        """Test using post method on "me" view should return
        error.
        """
        res = self.client.post(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile with validated data
        is successful.
        """
        payload = {
            'email': 'newemail@gmail.com',
            'password': 'new_passowrd',
            'name': 'new_name'
        }
        res = self.client.patch(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))
