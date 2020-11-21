from django.db import models
from django.contrib.auth import get_user_model
from users.models import CustomUser


User = get_user_model()


class Category(models.Model):
    name = models.CharField(blank=False, null=False, max_length=200)
    slug = models.SlugField(blank=False, null=False, max_length=60, unique=True)


class Genre(models.Model):
    name = models.CharField(blank=False, null=False, max_length=200)
    slug = models.SlugField(blank=False, null=False, max_length=60, unique=True)


class Title(models.Model):
    name = models.CharField(blank=False, null=False, max_length=200)
    year = models.IntegerField(blank=False, null=False)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, blank=True, null=True,
        related_name='titles',
        on_delete=models.SET_NULL
    )
    genre = models.ManyToManyField(Genre, blank=True)


class Reviews(models.Model):
    SCORE_CHOICES = (
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'),
        (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'),
    )

    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
    author = models.ForeignKey(
        CustomUser, blank=False, null=False, max_length=200, on_delete=models.CASCADE,
        related_name='review_author',
    )
    title = models.ForeignKey(
        Title, blank=False, null=False, on_delete=models.CASCADE,
        related_name='review'
    )
    text = models.TextField(blank=False, null=False, max_length=2000)
    pub_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('author', 'title')


class Comments(models.Model):
    author = models.ForeignKey(
        CustomUser, blank=False, null=False, max_length=200,
        related_name='comments', on_delete=models.CASCADE,
    )
    text = models.CharField(blank=False, null=False, max_length=200)
    review = models.ForeignKey(
        Reviews, on_delete=models.CASCADE,
        related_name='comments',
        blank=False, null=False
    )
    pub_date = models.DateTimeField(auto_now=True)
