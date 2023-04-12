from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    """用户拓展信息"""
    department = models.ForeignKey('Department', blank=True, null=True, help_text='部门', verbose_name='部门',
                                   on_delete=models.SET_NULL, related_name="section_users")
    group_extensions = models.ManyToManyField('GroupExtension', help_text='角色', related_name='group_users')
    permissions = models.ManyToManyField('Permissions', help_text='角色权限', blank=True)
    phone_number = models.CharField(max_length=11, help_text='手机号', verbose_name='手机号', default='')
    id_card_num = models.CharField(max_length=18, help_text='身份证号码', default='')
    delete_date = models.DateTimeField(blank=True, null=True,
                                       help_text='删除日期', verbose_name='删除日期')
    delete_flag = models.BooleanField(help_text='是否删除', verbose_name='是否删除', default=False)
    created_user = models.ForeignKey('self', blank=True, null=True, related_name='c_%(app_label)s_%(class)s_related',
                                     help_text='创建人', verbose_name='创建人', on_delete=models.SET_NULL,
                                     related_query_name='c_%(app_label)s_%(class)ss')
    last_updated_user = models.ForeignKey('self', blank=True, null=True,
                                          related_name='u_%(app_label)s_%(class)s_related',
                                          help_text='更新人', verbose_name='更新人', on_delete=models.SET_NULL,
                                          related_query_name='u_%(app_label)s_%(class)ss')
    delete_user = models.ForeignKey('self', blank=True, null=True, related_name='d_%(app_label)s_%(class)s_related',
                                    help_text='删除人', verbose_name='删除人', on_delete=models.SET_NULL,
                                    related_query_name='d_%(app_label)s_%(class)ss')
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_updated_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    def __str__(self):
        return "{}".format(self.username)

    class Meta:
        db_table = "user"
        verbose_name_plural = verbose_name = '用户'


class AbstractEntity(models.Model):
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_updated_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    created_user = models.ForeignKey(User, blank=True, null=True, related_name='c_%(app_label)s_%(class)s_related',
                                     help_text='创建人', verbose_name='创建人', on_delete=models.SET_NULL,
                                     related_query_name='c_%(app_label)s_%(class)ss')
    last_updated_user = models.ForeignKey(User, blank=True, null=True, related_name='u_%(app_label)s_%(class)s_related',
                                          help_text='更新人', verbose_name='更新人', on_delete=models.SET_NULL,
                                          related_query_name='u_%(app_label)s_%(class)ss')
    delete_user = models.ForeignKey(User, blank=True, null=True, related_name='d_%(app_label)s_%(class)s_related',
                                    help_text='删除人', verbose_name='删除人', on_delete=models.SET_NULL,
                                    related_query_name='d_%(app_label)s_%(class)ss')
    delete_time = models.DateTimeField(blank=True, null=True,
                                       help_text='删除日期', verbose_name='删除日期')
    delete_flag = models.BooleanField(help_text='是否删除', verbose_name='是否删除', default=False)

    class Meta(object):
        abstract = True


class Department(AbstractEntity):
    """部门表"""
    name = models.CharField(max_length=30, help_text='部门名称', verbose_name='部门名称')
    parent_section = models.ForeignKey('self', help_text='父节点部门', on_delete=models.PROTECT,
                                       related_name='children_sections', blank=True, null=True)
    in_charge_user = models.ForeignKey(User, help_text='负责人', blank=True, null=True, on_delete=models.SET_NULL,
                                       related_name='in_charge_sections')

    def __str__(self):
        return self.name

    def total_children_sections(self):
        department_ids = []
        s_id = [self.id]
        department_ids += s_id
        while s_id:
            s_id = Department.objects.filter(parent_section_id__in=s_id).values_list('id', flat=True)
            department_ids += s_id
        return department_ids

    class Meta:
        db_table = 'department'
        verbose_name_plural = verbose_name = '部门'


class Permissions(models.Model):
    code = models.CharField(max_length=64, help_text='权限代码', unique=True)
    name = models.CharField(max_length=64, help_text='权限名称')
    parent = models.ForeignKey('self', help_text='父节点', related_name='children_permissions',
                               blank=True, null=True, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=16, help_text='所属模块', blank=True, null=True)

    @property
    def children_list(self):
        return list(self.children_permissions.values('id', 'code', 'name'))

    class Meta:
        db_table = 'permissions'
        verbose_name_plural = verbose_name = '权限'


class GroupExtension(AbstractEntity):
    """角色"""
    group_code = models.CharField(max_length=50, help_text='角色代码', verbose_name='角色代码', unique=True)
    name = models.CharField('角色名称', max_length=150, unique=True)
    is_used = models.BooleanField(help_text='是否使用', verbose_name='是否使用', default=True)
    permissions = models.ManyToManyField(Permissions, help_text='角色权限', blank=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        db_table = 'group_extensions'
        verbose_name_plural = verbose_name = '角色'


class UserOperationLog(models.Model):
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    operator_user = models.CharField(max_length=64, help_text='操作人')
    operator_type = models.CharField(max_length=64, help_text='操作类型')
    operator_reason = models.CharField(max_length=64, help_text='操作原因')
    operation_desc = models.JSONField(help_text='操作描述', null=True, blank=True)

    class Meta:
        db_table = 'user_operation_log'
        verbose_name_plural = verbose_name = '用户操作履历'

