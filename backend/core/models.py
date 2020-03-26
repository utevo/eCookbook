import os
import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """Create and saves a new user"""
        if not email:
            raise ValueError('User need to have an email address')

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **kwargs):
        """Create and saves a new superuser"""
        superuser = self.create_user(email, password, **kwargs)
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that using email insted of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


def recipe_image_path(instance, filename):
    _, ext = os.path.splitext(filename)
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads/recipes/', filename)


class Recipe(models.Model):

    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price_dolars = models.DecimalField(max_digits=10, decimal_places=2)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    images = models.ImageField(null=True, upload_to=recipe_image_path)

    def __str__(self):
        return self.title
