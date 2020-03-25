from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Ingredient, Recipe

from recipes.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse("recipes:recipe-list")


def detail_recipe_url(recipe_id):
    return reverse('recipes:recipe-detail', args=[recipe_id])


def create_user(email, password):
    return get_user_model().objects.create_user(email=email, password=password)


def sample_tag(user, name='Simple tag'):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Simple ingredient'):
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    defaults = {
        "title": "Simple recipe",
        "time_minutes": 45,
        "price_dolars": 10.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that authentication is needed for retriving tags"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesAPITests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test@gmail.com", password="test_password"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_recipes(self):
        """Test retrieving tags"""
        sample_recipe(user=self.user, title="Tomato Soup", time_minutes=25)
        sample_recipe(
            user=self.user, title="Delicious Beef", price_dolars=11.25
        )

        recipes = Recipe.objects.all().order_by('-title')
        serializer = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_only_user_recipe(self):
        """Test that only user tags are retrieved"""
        sample_recipe(user=self.user, title="Tomato Soup", time_minutes=25)
        sample_recipe(
            user=self.user, title="Delicious Beef", price_dolars=11.25
        )

        other_user = create_user(
            email="other@gmail.com", password="other_password"
        )
        sample_recipe(user=other_user, title="Orange Cake", time_minutes=60)
        sample_recipe(
            user=other_user, title="Mac & Cheese", price_dolars=4.50
        )

        recipes = Recipe.objects.filter(user=self.user).order_by('-title')
        serializer = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_detail_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        serializer = RecipeDetailSerializer(recipe)

        url = detail_recipe_url(recipe.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
