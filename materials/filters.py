import django_filters

from materials.models import Material


class MaterialFilter(django_filters.rest_framework.FilterSet):
    project_code = django_filters.CharFilter(field_name='project_code', lookup_expr='icontains')
    project_name = django_filters.CharFilter(field_name='project_name', lookup_expr='icontains')
    inventory_code = django_filters.CharFilter(field_name='inventory_code', lookup_expr='icontains')
    inventory_name = django_filters.CharFilter(field_name='inventory_name', lookup_expr='icontains')
    specification = django_filters.CharFilter(field_name='specification', lookup_expr='icontains')

    class Meta:
        model = Material
        fields = ('id', 'project_code', 'project_name', 'inventory_code', 'inventory_name', 'specification')
