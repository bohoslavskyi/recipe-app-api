from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import User


class AdminSiteTest(TestCase):
    def setUp(self) -> None:
        self.client: Client = Client()
        self.admin_user: User = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin_user)
        self.user: User = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Teset User',
        )

    def test_users_list(self) -> None:
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_edit_user_page(self) -> None:
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self) -> None:
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
