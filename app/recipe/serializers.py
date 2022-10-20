from core import models
from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = models.Recipe
        fields = [
            "id",
            "title",
            "price",
            "time_minutes",
            "link",
            "tags",
            "ingredients",
        ]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context["request"].user
        for tag in tags:
            tag_obj, created = models.Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        auth_user = self.context["request"].user
        for ingredient in ingredients:
            ingredient_obj, created = models.Ingredient.objects.get_or_create(
                user=auth_user, **ingredient
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        recipe = models.Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
