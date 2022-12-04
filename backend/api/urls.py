from django.urls import include, path, re_path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UsersViewSet
)

v1_router = routers.DefaultRouter()
v1_router.register('users', UsersViewSet, basename='users')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('tags', TagViewSet, basename='tags')

app_name = 'api'

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
