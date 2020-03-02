from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            'admin@gmail.com',
            'password'
        )
        self.client.force_login(self.superuser)
        self.user = get_user_model().objects.create_user(
            'user@gmail.com',
            'password'
        )

    def test_users_page(self):
        """Test that users are listed on users page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_page(self):
        """Test that the user change page works"""
        url = reverse('admin:core_user_change', args=(self.user.id,))
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
