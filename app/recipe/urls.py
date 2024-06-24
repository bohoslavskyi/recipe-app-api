from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views


router: DefaultRouter = DefaultRouter()
router.register(prefix='recipes', viewset=views.RecipeViewSet)
router.register(prefix='tags', viewset=views.TagViewSet)

app_name: str = 'recipe'

urlpatterns: list = [
    path(route='', view=include(router.urls)),
]
