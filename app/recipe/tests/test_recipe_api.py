from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, User
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id: int) -> str:
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user: User, **params: dict) -> Recipe:
    defaults: dict = {
        'title': 'Sample recipe title',
        'description': 'Sample recipe description',
        'price': Decimal('5.49'),
        'time_minutes': 25,
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def create_user(**params: dict) -> User:
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPItests(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

    def test_auth_required(self) -> None:
        response: HttpResponse = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.user: User = create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self) -> None:
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response: HttpResponse = self.client.get(RECIPES_URL)
        recipes: list[Recipe] = Recipe.objects.all().order_by('-id')
        serializer: RecipeSerializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_list_limited_to_user(self) -> None:
        other_user: User = create_user(
            email='other@example.com',
            password='testpass123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        response: HttpResponse = self.client.get(RECIPES_URL)
        recipes: list[Recipe] = Recipe.objects.filter(user=self.user)
        serializer: RecipeSerializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_recipe_detail(self) -> None:
        recipe: Recipe = create_recipe(user=self.user)
        url: str = detail_url(recipe.id)
        response: HttpResponse = self.client.get(url)
        serializer: RecipeDetailSerializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self) -> None:
        payload: dict = {
            'title': 'Sample recipe title',
            'price': Decimal('5.49'),
            'time_minutes': 30,
        }
        response: HttpResponse = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe: Recipe = Recipe.objects.get(id=response.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_pastial_update(self) -> None:
        original_link: str = 'http://example.com/recipe.pdf'
        recipe: Recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )
        payload = {
            'title': 'New sample recipe title'
        }
        url: str = detail_url(recipe.id)
        response: HttpResponse = self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)

    def test_full_update(self) -> None:
        recipe: Recipe = create_recipe(user=self.user)
        payload: dict = {
            'title': 'New sample recipe title',
            'description': 'New sample recipe description',
            'price': Decimal('10.00'),
            'time_minutes': 15,
            'link': 'http://example.com/new_recipe.pdf',
        }
        url: str = detail_url(recipe.id)
        response: HttpResponse = self.client.put(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self) -> None:
        new_user: User = create_user(
            email='new.user@example.com',
            password='testpass123',
        )
        recipe: Recipe = create_recipe(user=self.user)
        payload: dict = {
            'user': new_user.id,
        }
        url: str = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self) -> None:
        recipe: Recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        response: HttpResponse = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
