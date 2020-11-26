from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import GenreViewSet, CategoryViewSet, TitleViewSet, \
    UserViewSet, ReviewsViewSet, register, token, CommentsViewSet

v1_router = DefaultRouter()
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('users', UserViewSet, basename='users')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewsViewSet, basename='reviews')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments'
)

urlpatterns = [
    path('v1/auth/email/', register, name='register'),
    path('v1/auth/token/', token, name='token'),
    path('v1/', include(v1_router.urls)),
]
