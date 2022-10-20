from core.models import Recipe, Tag
from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe.serializers import (
    RecipeDetailSerializer,
    RecipeSerializer,
    TagSerializer,
)

# Create your views here.


class RecipeViewSet(viewsets.ModelViewSet):

    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-name")
