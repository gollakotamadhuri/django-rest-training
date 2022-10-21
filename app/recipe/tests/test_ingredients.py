from core.models import Ingredient, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import IngredientSerializer
from rest_framework import status
from rest_framework.test import APIClient

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="sampleuser@example.com", password="samplepass"):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_ingredients(self):
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_get_ingredients(self):
        Ingredient.objects.create(user=self.user, name="Paneer")
        Ingredient.objects.create(user=self.user, name="Tomatoes")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        other_user = create_user(
            email="testuser001@example.com", password="testpass"
        )
        Ingredient.objects.create(user=other_user, name="Hing")
        ig2 = Ingredient.objects.create(user=self.user, name="Almonds")

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ig2.name)

    def test_update_ingredients(self):
        ingredient = Ingredient.objects.create(user=self.user, name="Grapes")
        url = detail_url(ingredient.id)

        payload = {"name": "Oranges"}

        res = self.client.patch(url, payload, format="json")
        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredients(self):
        ingredient = Ingredient.objects.create(
            user=self.user, name="Chocolate"
        )
        url = detail_url(ingredient.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id))

    def test_filter_ingredients_assigned(self):
        ing1 = Ingredient.objects.create(user=self.user, name="Carrots")
        ing2 = Ingredient.objects.create(user=self.user, name="Chocolate")
        recipe = Recipe.objects.create(
            user=self.user, title="Carrot Halwa", price="15", time_minutes=5
        )
        recipe.ingredients.add(ing1)

        params = {"assigned_only": 1}

        res = self.client.get(INGREDIENTS_URL, params)

        s1 = IngredientSerializer(ing1)
        s2 = IngredientSerializer(ing2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        ing = Ingredient.objects.create(user=self.user, name="Carrots")
        Ingredient.objects.create(user=self.user, name="Chocolate")
        r1 = Recipe.objects.create(
            user=self.user, title="Carrot Halwa", price="15", time_minutes=5
        )
        r1.ingredients.add(ing)
        r2 = Recipe.objects.create(
            user=self.user, title="Carrot Cake", price="15", time_minutes=5
        )
        r2.ingredients.add(ing)
        params = {"assigned_only": 1}
        res = self.client.get(INGREDIENTS_URL, params)
        self.assertEqual(len(res.data), 1)
