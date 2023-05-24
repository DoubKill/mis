from django.contrib.auth.models import AnonymousUser
from django.db.models import Max
from django.forms import model_to_dict
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from basics.models import GlobalCodeType, GlobalCode
from mis.settings import COMMON_READ_ONLY_FIELDS


class BaseModelSerializer(serializers.ModelSerializer):
    """封装字段值国际化功能后的模型类序列化器，需要用ModelSerializer请直接继承该类"""
    created_username = serializers.CharField(source='created_user.username', read_only=True, default='')
    last_update_username = serializers.CharField(source='last_updated_user.username', read_only=True, default='')

    def create(self, validated_data):
        """
        可供所有继承该序列化器的子类自动补充created_user
        :param validated_data:
        :return:
        """
        if self.Meta.model.__name__ in ["Permission", "Group"]:
            return super().create(validated_data)
        user = self.context["request"].user
        if isinstance(user, AnonymousUser):
            user = None
        validated_data.update(created_user=user)
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        可供所有继承该序列化器的子类自动补充updated_user
        :param instance:
        :param validated_data:
        :return:
        """
        if self.Meta.model.__name__ in ["Permission", "Group"]:
            return super().update(instance, validated_data)
        user = self.context["request"].user
        if isinstance(user, AnonymousUser):
            user = None
        validated_data.update(last_updated_user=user)
        return super().update(instance, validated_data)


class GlobalCodeTypeSerializer(BaseModelSerializer):
    """公共代码类型序列化器"""
    type_name = serializers.CharField(max_length=64,
                                      validators=[
                                          UniqueValidator(queryset=GlobalCodeType.objects.filter(delete_flag=False),
                                                          message='该代码类型名称已存在'),
                                      ])
    type_no = serializers.CharField(max_length=64,
                                    validators=[
                                        UniqueValidator(queryset=GlobalCodeType.objects.all(),
                                                        message='该代码类型编号已存在'),
                                    ])

    class Meta:
        model = GlobalCodeType
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.filter(delete_flag=False),
                fields=('type_name', 'use_flag'),
                message="该代码类型名称已存在"
            )
        ]


class GlobalCodeSerializer(BaseModelSerializer):
    """公共代码序列化器"""
    global_no = serializers.CharField(max_length=64, validators=[UniqueValidator(
        queryset=GlobalCode.objects.all(), message='该公共代码编号已存在')])

    @staticmethod
    def validate_global_type(global_type):
        if global_type.use_flag == 0:
            raise serializers.ValidationError('弃用状态的代码类型不可新建公共代码')
        return global_type

    def create(self, validated_data):
        validated_data.update(created_user=self.context["request"].user)
        instance = super().create(validated_data)
        # if 'use_flag' in validated_data:
        #     if validated_data['use_flag'] != 0:  # 不是启用状态，修改其use_flag为id
        #         instance.use_flag = instance.id
        #         instance.save()
        return instance

    def update(self, instance, validated_data):
        # if 'use_flag' in validated_data:
        #     if instance.use_flag != validated_data['use_flag']:
        #         if validated_data['use_flag'] != 0:  # 弃用
        #             validated_data['use_flag'] = instance.id
        validated_data.update(last_updated_user=self.context["request"].user)
        return super(GlobalCodeSerializer, self).update(instance, validated_data)

    class Meta:
        model = GlobalCode
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


