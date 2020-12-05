from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.decorators import api_view, action
from django.core.mail import send_mail
from . import permissions

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import CategorySerializer, GenreSerializer, \
    TitleSerializer, TitleReadSerializer, CommentsSerializer, ReviewsSerializer
from users.serializers import CustomUserSerializer
from .models import Category, Genre, Title, Reviews
from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsAdminNotModerator

User = get_user_model()
admin = User.Roles.ADMIN
moderator = User.Roles.MODERATOR


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('review__score'))
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return TitleReadSerializer
        return TitleSerializer


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminNotModerator,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    http_method_names = ['get', 'post', 'delete', 'patch']

    def perform_update(self, serializer):
        serializer.save()
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        role = self.request.data.get('role')
        if role is not None:
            user.is_staff = role == admin
        user.save()

    @action(detail=False,
            permission_classes=[IsAuthenticated, ], url_path='me')
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAuthenticated, ],
            methods=['patch'], url_path='me')
    def patch(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(role=user.role, raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    email = request.data.get('email')
    if email is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(email=email)
    send_mail(
        'Confirmation code',
        str(user.confirmation_code),
        None,
        [email, ],
        fail_silently=True
    )
    return Response({'email': email}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def token(request):
    email = request.data.get('email')
    confirmation_code = request.data.get('confirmation_code')
    if email is None or confirmation_code is None:
        return Response({'error': 'Email or confirmation code are wrong!'},
                        status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(User, email=email,
                             confirmation_code=confirmation_code)
    if not user:
        return Response({'error': 'User does not exist!'},
                        status=status.HTTP_400_BAD_REQUEST)
    access_token = get_tokens_for_user(user)['access']
    return Response({'token': access_token}, status=status.HTTP_200_OK)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = [permissions.IsOwnerOrModerOrAdminOrReadOnly, ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review = generics.get_object_or_404(
            Reviews,
            pk=self.kwargs['review_id'],
            title_id=self.kwargs['title_id'],
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = generics.get_object_or_404(
            Reviews,
            pk=self.kwargs['review_id'],
            title_id=self.kwargs['title_id'],
        )
        serializer.save(
            author=self.request.user,
            review_id=review.pk,
        )


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    queryset = Reviews.objects.all()
    permission_classes = [permissions.IsOwnerOrModerOrAdminOrReadOnly, ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.review.all()

    def perform_create(self, serializers):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializers.save(author=self.request.user, title=title)
