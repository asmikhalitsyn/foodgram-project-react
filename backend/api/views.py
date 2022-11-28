from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, views, viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import IngredientFilter, TagFilter
from recipes.models import (
    Favorite,
    Tag,
    Ingredient,
    IngredientsInRecipe,
    Recipe,
    ShoppingCart
)
from .paginations import CustomPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AddRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    TagSerializer
)
from .utils import convert_txt
from users.models import CustomUser, Subscription


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TagFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return AddRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))
        return convert_txt(ingredients)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, pk)
        else:
            return self.delete_recipe(ShoppingCart, request, pk)

    def add_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if model.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError('Рецепт уже добавлен')
        model.objects.create(recipe=recipe, user=user)
        serializer = ShortRecipeSerializer(recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        obj = get_object_or_404(model, recipe=recipe, user=user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, favorite_id):
        user = request.user
        data = {
            'recipe': favorite_id,
            'user': user.id
        }
        serializer = FavoriteSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, favorite_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=favorite_id)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()


class SubscribeView(views.APIView):
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        author = get_object_or_404(CustomUser, pk=pk)
        user = self.request.user
        data = {
            'author': author.id,
            'user': user.id
        }
        serializer = SubscribeSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, pk):
        author = get_object_or_404(CustomUser, pk=pk)
        user = self.request.user
        subscription = get_object_or_404(
            Subscription,
            user=user,
            author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
