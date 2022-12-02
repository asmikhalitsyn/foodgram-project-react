from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    TagRecipe,
    ShoppingList,
    Tag
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('tag', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    list_filter = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favorite_count',)
    search_fields = ('author', 'name',)
    list_filter = ('author', 'name', 'tags',)

    def favorite_count(self, obj):
        return obj.favorite_recipe.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_filter = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)


@admin.register(ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_filter = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)
