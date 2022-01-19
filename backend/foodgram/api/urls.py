from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingList, FavoritesListViewSet, FollowViewSet,
                    IngredientViewSet, ShoppingListView, TagViewSet,
                    RecipeViewSet)

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('users/subscriptions/', FollowViewSet.as_view({'get': 'list'}),
         name='subscriptions'),
    path('users/<int:author_id>/subscribe/',
         FollowViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='subscribe'),
    path('recipes/<int:recipe_id>/favorite/', FavoritesListViewSet.as_view(),
         name='favorites_list'),
    path('recipes/<int:recipe_id>/shopping_cart/', ShoppingListView.as_view(),
         name='shopping_cart'),
    path('recipes/download_shopping_cart/', DownloadShoppingList.as_view(),
         name='download_shopping_cart'),
]