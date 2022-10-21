from core.models import Recipe, Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAG_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="sampleuser@example.com", password="samplepass"):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_filtered_tags(self):
        other_user = create_user(
            email="user2@example.com", password="password2"
        )
        Tag.objects.create(user=other_user, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Spicy")

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name="After Dinner")

        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name="Breakfast")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned(self):
        tag1 = Tag.objects.create(user=self.user, name="Sweet")
        tag2 = Tag.objects.create(user=self.user, name="Dessert")
        recipe = Recipe.objects.create(
            user=self.user, title="Carrot Halwa", price="15", time_minutes=5
        )
        recipe.tags.add(tag1)

        params = {"assigned_only": 1}

        res = self.client.get(TAG_URL, params)

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        tag = Tag.objects.create(user=self.user, name="Sweet")
        Tag.objects.create(user=self.user, name="Dessert")
        r1 = Recipe.objects.create(
            user=self.user, title="Carrot Halwa", price="15", time_minutes=5
        )
        r1.tags.add(tag)
        r2 = Recipe.objects.create(
            user=self.user, title="Carrot Cake", price="15", time_minutes=5
        )
        r2.tags.add(tag)
        params = {"assigned_only": 1}
        res = self.client.get(TAG_URL, params)
        self.assertEqual(len(res.data), 1)
