from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='email@gmail.com', password='test_password'):
    return get_user_model().objects.create_user(email, password)


class UserModelTests(TestCase):

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

    def test_create_user_without_email_unsuccesful(self):
        """Test creating user without email address raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'password')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        superuser = get_user_model().objects.create_superuser(
            'superuser@gmail.com',
            'password'
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)


class TagModelTests(TestCase):

    def test_tag_str(self):
        """Test the tag string representation."""

        tag = models.Tag.objects.create(
            name='Vegan',
            user=sample_user()
        )

        self.assertEqual(str(tag), tag.name)


class IngredientMidelTests(TestCase):

    def test_str(self):
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Spinach'
        )

        self.assertEqual(str(ingredient), ingredient.name)
