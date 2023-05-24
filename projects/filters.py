import django_filters
from projects.models import ProjectSummary


class ProblemFilter(django_filters.rest_framework.FilterSet):
    raise_date = django_filters.DateFromToRangeFilter(field_name='raise_date', help_text='提出日期', lookup_expr='range')
    unusual_item = django_filters.CharFilter(field_name='unusual_item', lookup_expr='icontains')
    explanation = django_filters.CharFilter(field_name='explanation', lookup_expr='icontains')
    department = django_filters.CharFilter(field_name='department', lookup_expr='icontains')
    project_name = django_filters.CharFilter(field_name='project_name', lookup_expr='icontains')

    class Meta:
        model = ProjectSummary
        fields = ('id', 'seq', 'raise_date', 'unusual_item', 'explanation', 'department', 'actual_date', 'status', 'project_name')
