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
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientSearchFilter, RecipeFilter
from .paginations import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    CreateResponseSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingListSerializer,
    SubscriptionShowSerializer,
    TagSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingList,
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
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    permission_classes = (permissions.AllowAny,)


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
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    )
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    filter_backends = [DjangoFilterBackend, ]

    def get_serializer_class(self):

        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def post_method_for_actions(request, pk, serializer_req):

        recipe = get_object_or_404(Recipe, pk=pk)
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer_req(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer_data = CreateResponseSerializer(recipe)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, pk, error, model):

        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'Рецепт удален из {error}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):

        if request.method == 'POST':
            return self.post_method_for_actions(request, pk,
                                                FavoriteSerializer)
        return self.delete_method_for_actions(request, pk,
                                              'избранного', Favorite)

    @action(methods=['post', 'delete'], detail=True, )
    def shopping_list(self, request, pk):

        if request.method == 'POST':
            return self.post_method_for_actions(request, pk,
                                                ShoppingListSerializer)
        return self.delete_method_for_actions(request, pk,
                                              'списка покупок', ShoppingList)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_list(self, request):

        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
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
