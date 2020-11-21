from django_filters import rest_framework as filters

from .models import Title


class TitleFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug')
    genre = filters.CharFilter(field_name='genre__slug')
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre')
