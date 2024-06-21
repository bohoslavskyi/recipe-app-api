from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, User
from recipe.serializers import RecipeSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def create_recipe(user: User, **params: dict) -> Recipe:
    defaults: dict = {
        'title': 'Sample recipe title',
        'description': 'Sample recipe description',
        'price': Decimal('5.49'),
        'time_minutes': 25,
        'link': 'http://example.com',
    }
    defaults.update(params)

    return Recipe(user=user, **defaults)


class PublicRecipeAPItests(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

    def test_auth_required(self) -> None:
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.user: User = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self) -> None:
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)
        recipes: list[Recipe] = Recipe.objects.all().order_by('-id')
        serializer: RecipeSerializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_list_limited_to_user(self) -> None:
        other_user: User = get_user_model().objects.create_user(
            email='other@example.com',
            password='testpass123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)
        recipes: list[Recipe] = Recipe.objects.filter(user=self.user)
        serializer: RecipeSerializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
