from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.paginations import CustomPagination
from api.permissions import (IsAuthenticatedFilterFavoritedAndShoppingCart,
                             IsAuthorAdminOrReadOnly)
from api.serializers import (CustomUserSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeSerializer,
                             ShoppingCartSerializer, ShowRecipeSerializer,
                             ShowSubscribeSerializer, SubscribeSerializer,
                             TagSerializer, WriteRecipeSerializer)
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Subscribe, Tag, User)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = WriteRecipeSerializer
    permission_classes = (
        IsAuthenticatedFilterFavoritedAndShoppingCart,
        IsAuthorAdminOrReadOnly,
        IsAuthenticatedOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return RecipeSerializer
        return WriteRecipeSerializer

    @staticmethod
    def create_object_in_action(serializer, pk):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        show_serializer = ShowRecipeSerializer(
            Recipe.objects.get(id=pk)
        )
        return Response(
            show_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def delete_object_in_action(model, user, recipe):
        get_object_or_404(
            model, user=user, recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredient = IngredientRecipe.objects.filter(
            recipe__shoppingcarts__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(
            summ_amount=Sum('amount')
        )
        name = ingredient.values_list(
            'ingredient__name',
            flat=True
        )
        measurement_unit = ingredient.values_list(
            'ingredient__measurement_unit',
            flat=True
        )
        amount = ingredient.values_list(
            'summ_amount',
            flat=True
        )
        shopping_cart = [f'Список покупок для {user}:\n\n']
        for i in range(len(name)):
            shopping_cart.append(
                f'{name[i]} ({measurement_unit[i]}) - {amount[i]}\n'
            )
        response = HttpResponse(shopping_cart)
        response['Content-Type'] = 'text/plain'
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'recipe': recipe.id,
            'user': user.id
        }
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(data=data)
            return self.create_object_in_action(serializer, pk)
        return self.delete_object_in_action(ShoppingCart, user, recipe)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'recipe': recipe.id,
            'user': user.id
        }
        if request.method == 'POST':
            serializer = FavoriteSerializer(data=data)
            return self.create_object_in_action(serializer, pk)
        return self.delete_object_in_action(Favorite, user, recipe)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (
        IsAuthorAdminOrReadOnly,
        IsAuthenticatedOrReadOnly,
    )
    pagination_class = CustomPagination

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        subscribing = User.objects.filter(subscribing__user=user)
        page = self.paginate_queryset(subscribing)
        serializer = ShowSubscribeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        subscribing = get_object_or_404(User, id=id)
        data = {
            'subscribing': subscribing.id,
            'user': user.id
        }
        if request.method == 'POST':
            serializer = SubscribeSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            show_serializer = ShowSubscribeSerializer(
                User.objects.get(id=id),
                context={'request': request}
            )
            return Response(
                show_serializer.data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(
            Subscribe,
            user=user,
            subscribing=subscribing
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
