from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class RecipeInFavoritesAndShoppingListViewSet(mixins.CreateModelMixin,
                                              mixins.DestroyModelMixin,
                                              mixins.ListModelMixin,
                                              mixins.RetrieveModelMixin,
                                              viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['recipe'] = kwargs.get('recipe_id')
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        user = request.user.id
        recipe = kwargs.get('recipe_id')
        instance = get_object_or_404(
            self.Meta.model, user=user, recipe=recipe
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
