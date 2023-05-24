from django.db import models

# Create your models here.
from user.models import AbstractEntity


class GlobalCodeType(AbstractEntity):
    """公共代码类型表"""
    type_no = models.CharField(max_length=64, help_text='类型编号', verbose_name='类型编号', unique=True)
    type_name = models.CharField(max_length=64, help_text='类型名称', verbose_name='类型名称')
    description = models.CharField(max_length=256, blank=True, null=True, help_text='说明', verbose_name='说明')
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)

    def __str__(self):
        return self.type_name

    class Meta:
        db_table = 'bdm_global_code_type'
        verbose_name_plural = verbose_name = '公共代码类型'


class GlobalCode(AbstractEntity):
    """公共代码表"""
    global_type = models.ForeignKey('GlobalCodeType', models.PROTECT, related_name="global_codes",
                                    help_text='全局类型ID', verbose_name='全局类型ID')
    global_no = models.CharField(max_length=64, help_text='公共代码编号', verbose_name='公共代码编号', unique=True)
    global_name = models.CharField(max_length=64, help_text='公用代码名称', verbose_name='公用代码名称')
    description = models.CharField(max_length=256, blank=True, null=True,
                                   help_text='说明', verbose_name='说明')
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)
    seq = models.IntegerField(help_text='排序', verbose_name='排序', default=1)

    def __str__(self):
        return self.global_name

    class Meta:
        db_table = 'bdm_global_code'
        verbose_name_plural = verbose_name = '公共代码'

