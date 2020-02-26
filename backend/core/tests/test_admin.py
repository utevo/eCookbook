from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.cient = Client()
        self.superuser = get_user_model().objects.create_superuser(
            'admin@gmail.com',
            'password'
        )
        self.client.force_login(self.superuser)
        self.user = get_user_model().objects.create_user(
            'user@gmail.com',
            'password'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)