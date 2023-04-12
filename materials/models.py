from django.db import models

# Create your models here.
from user.models import AbstractEntity


class Material(AbstractEntity):
    seq = models.IntegerField(help_text='序号', null=True, blank=True)
    choice = models.CharField(max_length=256, help_text='选择', null=True, blank=True)
    business_type = models.CharField(max_length=256, help_text='业务类型', null=True, blank=True)
    order_id = models.CharField(max_length=256, help_text='订单编号', null=True, blank=True)
    f_date = models.DateField(help_text='日期', null=True, blank=True)
    supplier = models.CharField(max_length=256, help_text='供应商', null=True, blank=True)
    department = models.CharField(max_length=256, help_text='部门', null=True, blank=True)
    salesman = models.CharField(max_length=256, help_text='业务员', null=True, blank=True)
    currency = models.CharField(max_length=256, help_text='币种', null=True, blank=True)
    inventory_code = models.CharField(max_length=256, help_text='存货编码', null=True, blank=True)
    inventory_name = models.CharField(max_length=256, help_text='存货名称', null=True, blank=True)
    specification = models.CharField(max_length=256, help_text='规格型号', null=True, blank=True)
    unit = models.CharField(max_length=256, help_text='主计量', null=True, blank=True)
    quantity = models.IntegerField(help_text='数量', null=True, blank=True)
    tax_unit_price = models.FloatField(help_text='原币含税单价', null=True, blank=True)
    unit_price = models.FloatField(help_text='原币单价', null=True, blank=True)
    amount = models.FloatField(help_text='原币金额', null=True, blank=True)
    tax_amount = models.FloatField(help_text='原币税额', null=True, blank=True)
    total_value_tax = models.FloatField(help_text='原币价税合计', null=True, blank=True)
    cumulative_export_quantity = models.FloatField(help_text='累计出口数量', null=True, blank=True)
    plan_arrive_date = models.DateField(help_text='计划到货日期', null=True, blank=True)
    project_code = models.CharField(max_length=256, help_text='项目编码', null=True, blank=True)
    project_name = models.CharField(max_length=256, help_text='项目名称', null=True, blank=True)
    documenter = models.CharField(max_length=256, help_text='制单人', null=True, blank=True)
    closers = models.CharField(max_length=256, help_text='行关闭人', null=True, blank=True)
    requirement_desc = models.CharField(max_length=256, help_text='需求分类代码说明', null=True, blank=True)
    pay_terms = models.CharField(max_length=256, help_text='付款条件', null=True, blank=True)
    tax_rate = models.FloatField(help_text='税率', null=True, blank=True)
    unbilled = models.FloatField(help_text='未开票量', null=True, blank=True)
    cumulative_billed = models.FloatField(help_text='累计开票量', null=True, blank=True)
    billing_status = models.CharField(max_length=256, help_text='开票状态', null=True, blank=True)

    class Meta:
        db_table = 'material'
        verbose_name_plural = verbose_name = '物料信息'


class MaterialSetting(AbstractEntity):
    display_columns = models.CharField(max_length=1024, help_text='显示列', null=True, blank=True)

    class Meta:
        db_table = 'material_setting'
        verbose_name_plural = verbose_name = '物料信息设定'


