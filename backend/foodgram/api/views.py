import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import utils, views
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import AuthorAndTagFilter, IngredientSearchFilter
from .paginations import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriptionShowSerializer,
    TagSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import Follow, User


class CustomTokenCreateView(views.TokenCreateView):

    def _action(self, serializer):
        super()._action(serializer)
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class UsersViewSet(UserViewSet):
    pagination_class = LimitOffsetPagination

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        recipes_limit = request.query_params['recipes_limit']
        authors = User.objects.filter(following__user=request.user)
        result_pages = self.paginate_queryset(
            queryset=authors
        )
        serializer = SubscriptionShowSerializer(
            result_pages,
            context={
                'request': request,
                'recipes_limit': recipes_limit
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id):

        if request.method != 'POST':
            subscription = Follow.objects.filter(
                user=request.user,
                following=get_object_or_404(User, id=id)
            )
            if subscription.exists():
                self.perform_destroy(subscription)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы уже отписаны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FollowSerializer(
            data={
                'user': request.user.id,
                'following': get_object_or_404(User, id=id).id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AuthorAndTagFilter

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST', 'PATCH']:
            return CreateRecipeSerializer
        return RecipeSerializer

    def add_delete_recipe_from_favorite_or_list(self, request,
                                                pk, model, recipe_model):
        user = request.user
        recipe = get_object_or_404(recipe_model, id=pk)
        if request.method == 'POST':
            if model.objects.filter(user=user,
                                    recipe=recipe).exists():
                return Response(
                    {'errors': f'{recipe.name} уже добавили'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe),
            return Response(
                FavoriteSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not model.objects.filter(user=user,
                                        recipe=recipe).exists():
                return Response(
                    {'errors': f'Нет такого рецепта {recipe.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.add_delete_recipe_from_favorite_or_list(
            request=request, pk=pk, model=Favorite,
            recipe_model=Recipe
        )

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.add_delete_recipe_from_favorite_or_list(
            request=request, pk=pk, model=ShoppingCart,
            recipe_model=Recipe
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):

        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount')).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'ingredient_amount')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="Shoppinglist.csv"')
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for item in list(ingredients):
            writer.writerow(item)
        return response
