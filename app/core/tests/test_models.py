"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class TestModel(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email: str = "test@example.com"
        password: str = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
