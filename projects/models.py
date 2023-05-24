from django.db import models

# Create your models here.
from user.models import AbstractEntity


class ProjectSummary(AbstractEntity):
    project_name = models.CharField(max_length=255, help_text='项目名称')
    problem_title = models.CharField(max_length=255, help_text='项目问题的标题', null=True, blank=True)
    seq = models.IntegerField(help_text='序号', null=True, blank=True)
    raise_date = models.DateField(help_text='提出日期', null=True, blank=True)
    unusual_item = models.CharField(max_length=255, help_text='异常项', null=True, blank=True)
    solution = models.CharField(max_length=255, help_text='解决措施', null=True, blank=True)
    explanation = models.CharField(max_length=255, help_text='说明', null=True, blank=True)
    department = models.CharField(max_length=255, help_text='负责部门', null=True, blank=True)
    hope_date = models.DateField(help_text='希望解决时间', null=True, blank=True)
    plan_date = models.DateField(help_text='计划解决时间', null=True, blank=True)
    actual_date = models.DateField(help_text='实际解决时间', null=True, blank=True)
    status = models.CharField(max_length=255, help_text='状态:完成、进行中、确认中、未开始、异常、跟踪中', null=True, blank=True)
    remark = models.CharField(max_length=255, help_text='备注', null=True, blank=True)
    times = models.IntegerField(help_text='次数', null=True, blank=True)

    class Meta:
        db_table = 'project_summary'
        verbose_name_plural = verbose_name = '项目问题汇总'


class ResourceAttachment(AbstractEntity):
    ATTENDANCE_TYPE = (
        (1, '图片'),
        (2, '视频'),
        (3, '文件'),
        (4, '其他')
    )
    project_summary = models.ForeignKey(ProjectSummary, on_delete=models.CASCADE, help_text='项目问题汇总', related_name='attachments')
    attachment_type = models.IntegerField(choices=ATTENDANCE_TYPE, help_text='附件类型')
    attachment_url = models.CharField(max_length=1024, help_text='附件路径', null=True, blank=True)

    class Meta:
        db_table = 'resource_attachment'
        verbose_name_plural = verbose_name = '项目附件资源'


class UploadResource(AbstractEntity):
    ownership = models.CharField(max_length=255, help_text='所属', null=True, blank=True)
    resource = models.FileField(upload_to='problem/%Y%m%d/', help_text='上传资源')
    upload_date = models.DateTimeField(auto_now_add=True, help_text='上传时间')

    class Meta:
        db_table = 'upload_resource'
        verbose_name_plural = verbose_name = '上传的资源'
