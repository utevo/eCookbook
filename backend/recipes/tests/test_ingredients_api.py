from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipes.serializers import IngredientSerializer


INGREDIENT_URL = reverse("recipes:ingredient-list")


def create_user(email, password):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test@gmail.com", password="test_password"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_list(self):
        Ingredient.objects.create(name="Spinash", user=self.user)
        Ingredient.objects.create(name="Cucumber", user=self.user)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_only_user_ingredients(self):
        """Test that only user ingredients are retrieved"""
        Ingredient.objects.create(name="Cucumber", user=self.user)
        Ingredient.objects.create(name="Tomato", user=self.user)

        other_user = create_user(
            email="other@gmail.com", password="other_password"
        )
        Ingredient.objects.create(name="Broccoli", user=other_user)
        Ingredient.objects.create(name="Carrot", user=other_user)

        ingredients = Ingredient.objects.filter(user=self.user).order_by(
            "-name"
        )
        serializer = IngredientSerializer(ingredients, many=True)

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_ingredient_successful(self):
        """Test creating a ingredient with valid data."""
        payload = {"name": "Tomato"}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user, name=payload["name"]
        ).exists()
        self.assertTrue(exists)

    def test_attemt_to_create_empty_ingredient(self):
        """Test creating a ingredient with empty name is unsuccessful."""
        payload = {"name": ""}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
