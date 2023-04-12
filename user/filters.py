import django_filters

from user.models import User, Department, GroupExtension, UserOperationLog


class UserFilter(django_filters.rest_framework.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains', help_text='用户名')
    groups = django_filters.CharFilter(field_name='group_extensions', help_text='角色id')
    department_name = django_filters.CharFilter(field_name='department__name', lookup_expr='icontains', help_text='部门')

    class Meta:
        model = User
        fields = ('username', 'groups', 'is_active', 'department_name', 'is_superuser')


class GroupExtensionFilter(django_filters.rest_framework.FilterSet):
    group_code = django_filters.CharFilter(field_name="group_code", lookup_expr="icontains", help_text="角色代码")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains", help_text="角色名称")

    class Meta:
        model = GroupExtension
        fields = {"group_code", "name", 'is_used'}


class DepartmentFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(field_name='name', help_text='名称', lookup_expr='icontains')
    department_id = django_filters.CharFilter(field_name='department_id', help_text="编码", lookup_expr='icontains')

    class Meta:
        model = Department
        fields = ('name', 'parent_section_id')


class UserOperationLogFilter(django_filters.rest_framework.FilterSet):
    operator_date = django_filters.DateFromToRangeFilter(field_name='create_time__date', help_text='操作日期', lookup_expr='range')
    operator_time = django_filters.TimeRangeFilter(field_name='create_time__time', help_text='操作时间', lookup_expr='range')
    operation_desc = django_filters.CharFilter(field_name='operation_desc', help_text='操作描述', lookup_expr='icontains')

    class Meta:
        model = UserOperationLog
        fields = ('operator_date', 'operator_time', 'operation_desc')

