from django.contrib import admin

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import User


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role'
    )
    list_filter = ('email', 'username')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorite_count',
    )
    list_filter = (
        'author',
        'name',
        'tags'
    )
    inlines = [IngredientRecipeInline]

    def favorite_count(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )
