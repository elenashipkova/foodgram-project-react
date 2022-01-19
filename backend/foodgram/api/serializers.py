from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (FavoritesList, Follow, Ingredient,
                            IngredientRecipe, Recipe, ShoppingList, Tag)
from users.models import User

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class GetIngredientInRecipeSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # amount = serializers.IntegerField()
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return FavoritesList.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = GetIngredientInRecipeSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate(self, data):
        # data = super().validate(data)
        ingredients = self.initial_data.get('ingredients')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше 0'
                )
        return data
           
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            IngredientRecipe.objects.update_or_create(
                recipe=recipe, ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        return recipe

    def update(self, instanse, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instanse.name = validated_data.get('name', instanse.name)
        instanse.text = validated_data.get('text', instanse.text)
        # instanse.image = validated_data.get('image', instanse.image)
        instanse.cooking_time = validated_data.get(
            'cooking_time', instanse.cooking_time
        )
        if validated_data.get('image') is not None:
            instanse.image = validated_data.get('image', instanse.image)

        IngredientRecipe.objects.filter(recipe=instanse).delete()

        for ingredient in ingredients:
            IngredientRecipe.objects.update_or_create(
                recipe=instanse, ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        
        instanse.tags.set(tags)
        instanse.save()
        return instanse


class FavoritesListSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoritesList
        fields = '__all__'

    def to_representation(self, obj):
        return {
            'id': obj.recipe.id,
            'name': obj.recipe.name,
            'image': obj.recipe.image.url,
            'cooking_time': obj.recipe.cooking_time,
        }


class ShoppingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = '__all__'

    def validate(self, data):
        user = data['user']
        recipe = data['recipe'].id
        if ShoppingList.objects.filter(user=user, recipe__id=recipe).exists():
            raise ValidationError('Рецепт уже добавлен в список покупок!')
        return data

    def to_representation(self, obj):
        return {
            'id': obj.recipe.id,
            'name': obj.recipe.name,
            'image': obj.recipe.image.url,
            'cooking_time': obj.recipe.cooking_time,
        }


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]

    def validate_author(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                'Вы не можете подписаться сами на себя!'
            )
        return value


class RecipeSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserFollowerSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSimpleSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = (
            'id', 'email', 'username', 'first_name', 'last_name'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=obj, author=request.user).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()
    