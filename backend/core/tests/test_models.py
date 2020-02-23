from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_succesful(self):
        """Test creating user with an email is succesful"""
        email = 'test@gmail.com'
        password = 'password'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test normalization of user's email address"""
        unnormalized_email = 'test@GmAiL.com'
        normalized_email = 'test@gmail.com'

        password = 'password'
        user = get_user_model().objects.create_user(
            email=unnormalized_email,
            password=password
        )

        self.assertEqual(normalized_email, user.email)