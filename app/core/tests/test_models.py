from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import User


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self) -> None:
        email: str = 'test@example.com'
        password: str = 'testpass123'
        user: User = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self) -> None:
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected_email in sample_emails:
            user: User = get_user_model().objects.create_user(
                email=email,
                password='sample123',
            )
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='',
            )

    def test_create_superuser(self) -> None:
        user: User = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='testpass123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
