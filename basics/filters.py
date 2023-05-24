import django_filters

from basics.models import GlobalCode, GlobalCodeType


class GlobalCodeTypeFilter(django_filters.rest_framework.FilterSet):
    type_no = django_filters.CharFilter(field_name='type_no', lookup_expr='icontains', help_text='代码编号')
    type_name = django_filters.CharFilter(field_name='type_name', lookup_expr='icontains', help_text='代码名称')
    use_flag = django_filters.BooleanFilter(field_name='use_flag', help_text='是否启用')
    class_name = django_filters.CharFilter(field_name='type_name', help_text='筛选班次')

    class Meta:
        model = GlobalCodeType
        fields = ('type_no', 'type_name', 'use_flag', 'class_name')


class GlobalCodeFilter(django_filters.rest_framework.FilterSet):
    class_name = django_filters.CharFilter(field_name='global_type__type_name', help_text='筛选班次')
    id = django_filters.CharFilter(field_name='global_type__id', help_text="全局代码类型id")
    type_no = django_filters.CharFilter(field_name='global_type__type_no', help_text="全局代码类型编码")
    use_flag = django_filters.NumberFilter(field_name='use_flag', help_text='0代表启用状态')

    class Meta:
        model = GlobalCode
        fields = ('class_name', 'id', 'type_no', 'use_flag')
