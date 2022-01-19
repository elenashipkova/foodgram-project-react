from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (FavoritesList, Follow, Ingredient,
                            IngredientRecipe, Recipe, ShoppingList, Tag)

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrAdmin
from .serializers import (FavoritesListSerializer, FollowSerializer,
                          IngredientSerializer,
                          RecipeCreateSerializer,
                          RecipeListSerializer, ShoppingListSerializer,
                          TagSerializer,
                          UserFollowerSerializer)

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
        data=request.data
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
            Follow, user=request.user.id,author=kwargs.get('author_id')
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoritesListViewSet(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }
        serializer = FavoritesListSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        FavoritesList.objects.get(user=user, recipe=recipe).delete()
        return Response(
            'Рецепт успешно удален из избранного',
            status.HTTP_204_NO_CONTENT
        )


class ShoppingListView(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }
        serializer = ShoppingListSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShoppingList.objects.get(user=user, recipe=recipe).delete()
        return Response(
            'Рецепт успешно удален из списка покупок',
            status.HTTP_204_NO_CONTENT
        )


class DownloadShoppingList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        final_list = {}

        ingredients = IngredientRecipe.objects.filter(recipe__shopping_cart__user=request.user)
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit

            if name not in final_list:
                final_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                final_list[name]['amount'] += amount

        download_list = []
        for item in final_list:
            download_list.append(f'{item} ({final_list[item]["measurement_unit"]}) - '
                                 f'{final_list[item]["amount"]} \n')
        filename = 'shopping_cart.txt'
        response = HttpResponse(download_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response