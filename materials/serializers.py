from rest_framework_jwt.settings import api_settings

from basics.serializers import BaseModelSerializer
from materials.models import Material, MaterialSetting
from mis.settings import COMMON_READ_ONLY_FIELDS

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class MaterialSerializer(BaseModelSerializer):

    def to_representation(self, instance):
        res = super().to_representation(instance)
        # 去除存货编码的小数点
        if res['inventory_code']:
            res['inventory_code'] = res['inventory_code'].rsplit('.', maxsplit=1)[0]
        return res

    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MaterialDisplaySerializer(BaseModelSerializer):

    class Meta:
        model = MaterialSetting
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS
