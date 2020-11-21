from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateAPIView
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
from .permissions import IsAdminOrReadOnly

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class CategoryViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
    permission_classes = (IsAdminUser,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    http_method_names = ['get', 'post', 'delete', 'patch']

    def perform_update(self, serializer):
        serializer.save()
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        if not self.request.data.get('role') is None:
            user.is_staff = self.request.data.get('role') in ('admin', 'moderator')
        user.save()


class UserSelfView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CustomUserSerializer
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(id=user.id)

    def get_object(self):
        queryset = self.get_queryset()
        user = self.request.user
        obj = get_object_or_404(queryset, id=user.id)
        self.check_object_permissions(self.request, obj)
        return obj


@api_view(['POST'])
def register(request):
    email = request.POST.get('email')
    if email is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(email=email)
    if not user:
        user = User.objects.create_user(email=email)
    send_mail(
        'Confirmation code',
        str(user.password),
        'from@example.com',
        [email, ],
        fail_silently=True
    )
    return Response({'email': email}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def token(request):
    email = request.POST['email']
    confirmation_code = request.POST['confirmation_code']
    if email is None or not User.objects.filter(email=email):
        return Response({'field_name': 'email'}, status=status.HTTP_400_BAD_REQUEST)
    if confirmation_code is None or not User.objects.filter(password=confirmation_code):
        return Response({'field_name': 'confirmation_code'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(email=email, password=confirmation_code)
    if not user:
        return Response({'field_name': 'user does not exist'}, status=status.HTTP_400_BAD_REQUEST)
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
        queryset = Reviews.objects.all()
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return queryset.filter(title=title)

    def perform_create(self, serializers):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializers.save(author=self.request.user, title=title)
