from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from basics.models import GlobalCode
from basics.serializers import BaseModelSerializer
from materials.models import Material, MaterialSetting
from mis.settings import COMMON_READ_ONLY_FIELDS

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class MaterialSerializer(BaseModelSerializer):

    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MaterialDisplaySerializer(BaseModelSerializer):

    def create(self, validated_data):
        display_columns = validated_data.get('display_columns', None)
        if not display_columns:
            raise serializers.ValidationError('至少选择一列!')
        columns = display_columns.split(',')
        # 获取默认排序
        g_set = list(GlobalCode.objects.filter(delete_flag=False, global_type__delete_flag=False, global_type__type_name='物料信息列顺序',
                                               description__in=columns).order_by('seq').values_list('description', flat=True))
        if not g_set:
            raise serializers.ValidationError('列顺序未设置!')
        if len(g_set) != len(columns):
            raise serializers.ValidationError('请检查列顺序公用代码设置！')
        validated_data['display_columns'] = ','.join(g_set)
        instance = super().create(validated_data)
        return instance

    class Meta:
        model = MaterialSetting
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS
