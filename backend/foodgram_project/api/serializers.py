import base64

import webcolors
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.paginations import ShowRecipePagination
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Subscribe, Tag)
from users.models import User


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context['request']
        user = request.user
        return Subscribe.objects.filter(
            user=user.id, subscribing=obj.id
        ).exists()


class UserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return webcolors.hex_to_name(data)


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    color = Hex2NameColor(read_only=True)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')
        model = Ingredient


class IngredientRecipeSerializer(IngredientSerializer):
    id = serializers.IntegerField(
        source='ingredient.id',
        read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class WriteIngredientRecipeSerializer(IngredientSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount'
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context['request']
        return Favorite.objects.filter(
            user=request.user.id, recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        return ShoppingCart.objects.filter(
            user=request.user.id, recipe=obj.id
        ).exists()


class WriteRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = WriteIngredientRecipeSerializer(
        many=True,
        source='ingredientrecipe_set'
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'author',
            'text',
            'cooking_time'
        )

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
                recipe=recipe
            )

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=author,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        instance.tags.set(tags)
        self.create_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class ShowRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    validators = [UniqueTogetherValidator(
        queryset=ShoppingCart.objects.all(),
        fields=('recipe', 'user'),
        message=('Рецепт уже добавлен в покупки')
    )]


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    validators = [UniqueTogetherValidator(
        queryset=Favorite.objects.all(),
        fields=('recipe', 'user'),
        message=('Рецепт уже добавлен в избранное')
    )]


class ShowSubscribeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context['request']
        recipes = Recipe.objects.filter(author=obj)
        paginator = ShowRecipePagination()
        recipes_limit = paginator.paginate_queryset(
            recipes, request
        )
        serializer = ShowRecipeSerializer(
            recipes_limit,
            many=True,
            context={'request': request}
        )
        return serializer.data


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('user', 'subscribing')

    validators = [UniqueTogetherValidator(
        queryset=Subscribe.objects.all(),
        fields=('subscribing', 'user'),
        message=('Подписка уже оформлена')
    )]

    def validate(self, data):
        if data['user'] == data['subscribing']:
            raise serializers.ValidationError(
                'На себя подписаться нельзя'
            )
        return data
