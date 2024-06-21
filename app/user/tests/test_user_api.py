from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import User


CREATE_USER_URL = reverse('user:create')
CREATE_TOKEN_URL = reverse('user:token')


def create_user(**params) -> User:
    return get_user_model().objects.create_user(**params)


class PublicUserAPITest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user_success(self) -> None:
        payload: dict = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_create_user_with_email_exists_error(self) -> None:
        payload: dict = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self) -> None:
        payload: dict = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self) -> None:
        user_details: dict = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password-123',
        }
        create_user(**user_details)

        payload: dict = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_token_bad_credentials(self) -> None:
        user_details: dict = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password-123',
        }
        create_user(**user_details)

        payload: dict = {
            'email': user_details['email'],
            'password': 'test-user-bad-password-123',
        }
        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_blank_password(self) -> None:
        payload: dict = {
            'email': 'test@example.com',
            'password': '',
        }
        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
