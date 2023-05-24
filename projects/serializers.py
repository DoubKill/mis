from django.db.models import Max
from django.db.transaction import atomic
from rest_framework import serializers

from basics.serializers import BaseModelSerializer
from mis.settings import COMMON_READ_ONLY_FIELDS
from projects.models import ProjectSummary, UploadResource, ResourceAttachment


class UploadResourceSerializer(BaseModelSerializer):

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res['resource'] = instance.resource.url
        return res

    def validate(self, attrs):
        resource = attrs.get('resource')
        if resource and round(resource.size / 1024 / 1024, 2) > 10:
            raise serializers.ValidationError('上传资源大小不能超过10M')
        return attrs

    class Meta:
        model = UploadResource
        fields = '__all__'


class ProblemSerializer(BaseModelSerializer):
    add_datas = serializers.ListField(required=False, allow_null=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        images, videos, files = [], [], []
        attachments = instance.attachments.exclude(attachment_type=4).order_by('id')
        for attachment in attachments:
            attachment_type, attachment_url = attachment.attachment_type, attachment.attachment_url
            if attachment_type == 1:
                images.append(attachment_url)
            elif attachment_type == 2:
                videos.append(attachment_url)
            elif attachment_type == 3:
                files.append(attachment_url)
            else:
                continue
        ret.update({'images': images, 'videos': videos, 'files': files})
        return ret

    def validate(self, attrs):
        all_status = self.context['all_status']
        all_departments = self.context['all_departments']
        status, department, times = attrs.get('status'), attrs.get('department'), attrs.get('times')
        if (status and status not in all_status) or (department and department not in all_departments):
            raise serializers.ValidationError('状态或部门不正确, 请配置后导入!')
        if not times:  # 新增记录, 否则为导入
            max_times = ProjectSummary.objects.filter(project_name=attrs['project_name']).aggregate(max_times=Max('times'))['max_times']
            attrs['times'] = 1 if not max_times else max_times
        return attrs

    @atomic
    def create(self, validated_data):
        add_datas = validated_data.pop('add_datas', [])
        instance = super().create(validated_data)
        if add_datas:
            ResourceAttachment.objects.bulk_create([ResourceAttachment(**data, project_summary=instance) for data in add_datas])
        return instance

    class Meta:
        model = ProjectSummary
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProblemUpdateSerializer(BaseModelSerializer):
    add_datas = serializers.ListField(required=False, allow_null=True)


    @atomic
    def update(self, instance, validated_data):
        add_datas = validated_data.pop('add_datas', [])
        instance.attachments.all().delete()
        if add_datas:
            ResourceAttachment.objects.bulk_create([ResourceAttachment(**data, project_summary=instance) for data in add_datas])
        instance = super().update(instance, validated_data)
        return instance

    class Meta:
        model = ProjectSummary
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS
