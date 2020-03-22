from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipes.serializers import TagSerializer


TAGS_URL = reverse("recipes:tag-list")


def create_user(email, password):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsAPITests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that authentication is needed for retriving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test the privately available tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="email@gmail.com", password="test_password"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(name="Dessert", user=self.user)
        Tag.objects.create(name="Italian", user=self.user)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_only_user_tags(self):
        """Test that only user tags are retrieved"""
        Tag.objects.create(name="Dessert", user=self.user)
        Tag.objects.create(name="Italian", user=self.user)

        other_user = create_user(
            email="other@gmail.com", password="other_password"
        )
        Tag.objects.create(name="Vegan", user=other_user)
        Tag.objects.create(name="Keto", user=other_user)

        tags = Tag.objects.filter(user=self.user).order_by("-name")
        serializer = TagSerializer(tags, many=True)

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_tag_successful(self):
        """Test creating a tag with valid data."""
        payload = {"name": "Vegan"}
        self.client.post(TAGS_URL, payload)

        tag = Tag.objects.filter(user=self.user, name=payload["name"])
        self.assertEqual(len(tag), 1)

    def test_attemt_to_create_empty_tag(self):
        """Test creating a tag with empty name is unsuccessful."""
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
