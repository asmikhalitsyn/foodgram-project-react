from django_filters import FilterSet
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    author = filters.CharFilter(
        field_name='author__id',
        lookup_expr='icontains'
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='get_is_favorited',
    )
    is_in_shopping_list = filters.BooleanFilter(
        method='get_is_in_shopping_list'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    def get_is_favorited(self, queryset, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def get_is_in_shopping_list(self, queryset, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_list']


class IngredientSearchFilter(filters.FilterSet):

    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name', )
