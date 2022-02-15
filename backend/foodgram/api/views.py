from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (FavoritesList, Follow, Ingredient,
                            IngredientRecipe, Recipe, ShoppingList, Tag)
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .mixins import RecipeInFavoritesAndShoppingListViewSet
from .permissions import IsAuthorOrAdmin
from .serializers import (FavoritesListSerializer, FollowSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, ShoppingListSerializer,
                          TagSerializer, UserFollowerSerializer)

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdmin,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return RecipeCreateSerializer


class FollowViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list']:
            return UserFollowerSerializer
        return FollowSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        data['author'] = kwargs.get('author_id')
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Follow, user=request.user.id, author=kwargs.get('author_id')
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoritesListViewSet(RecipeInFavoritesAndShoppingListViewSet):
    queryset = FavoritesList.objects.order_by('-recipe__pub_date')
    serializer_class = FavoritesListSerializer

    class Meta:
        model = FavoritesList


class ShoppingListViewSet(RecipeInFavoritesAndShoppingListViewSet):
    queryset = ShoppingList.objects.order_by('-created')
    serializer_class = ShoppingListSerializer

    class Meta:
        model = ShoppingList


class DownloadShoppingList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        shop_list = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    amount=Sum('amount'))

        filename = 'shopping_cart.txt'
        response = HttpResponse(shop_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
