from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagsViewSet,
    SubscriptionViewSet,
    SubscribeView, FavoriteView
)

v1_router = routers.DefaultRouter()
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('tags', TagsViewSet, basename='tags')

app_name = 'api'

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include(v1_router.urls)),
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path('recipes/<int:favorite_id>/favorite/', FavoriteView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:pk>/subscribe/', SubscribeView.as_view()),
]
