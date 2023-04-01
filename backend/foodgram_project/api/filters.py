from django_filters import rest_framework

from recipes.models import Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    author = rest_framework.CharFilter(
        field_name='author__username',
    )
    is_favorited = rest_framework.filters.NumberFilter(
        method='is_favorited_filter'
    )
    is_in_shopping_cart = rest_framework.filters.NumberFilter(
        method='is_in_shopping_cart_filter'
    )

    def is_favorited_filter(self, queryset, name, value):
        if bool(value):
            return queryset.filter(
                favorites__user=self.request.user
            )
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if bool(value):
            return queryset.filter(
                shoppingcarts__user=self.request.user
            )
        return queryset

    class Meta:
        model = Recipe
        fields = {
            'author',
            'tags'
        }
