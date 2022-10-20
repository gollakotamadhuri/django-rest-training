from decimal import Decimal

from core import models
from django.contrib.auth import get_user_model
from django.test import TestCase


def create_user(email="sample@example.com", password="samplepass"):
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """Tests models"""

    def test_create_user_with_email(self):
        """Check if user is created correctly"""
        user_email = "test@example.com"
        user_password = "testpassword123"

        user = get_user_model().objects.create_user(
            email=user_email, password=user_password
        )

        self.assertEqual(user.email, user_email)
        self.assertTrue(user.check_password(user_password))

    def test_check_if_email_normalized(self):
        """Tests if user email is normalized"""
        test_users = [
            ["testuser@example.com", "testuser@example.com"],
            ["Testuser@EXAMPLE.com", "Testuser@example.com"],
            ["TESTUSER@example.COM", "TESTUSER@example.com"],
            ["testUser@Example.Com", "testUser@example.com"],
        ]

        for input, expected in test_users:
            user = get_user_model().objects.create_user(
                email=input, password="testpassword"
            )
            self.assertEqual(user.email, expected)

    def test_check_for_null_email(self):
        """Tests for null email id inputs"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email="", password="testpassword123"
            )

    def test_create_superuser(self):
        """Tests if a superuser is created successfully"""
        user_email = "admin@example.com"
        user_password = "adminpassword1234"
        user = get_user_model().objects.create_superuser(
            email=user_email, password=user_password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        user = get_user_model().objects.create_user(
            email="testuser003@example.com", password="testpass003"
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Recipe Title",
            time_minutes=5,
            price=Decimal(5.5),
            description="Sample recipe description",
        )

        self.assertTrue(str(recipe), recipe.title)

    def test_create_tag(self):
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user, name="Ingredient1"
        )
        self.assertEqual(str(ingredient), ingredient.name)
