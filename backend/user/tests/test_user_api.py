from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


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
