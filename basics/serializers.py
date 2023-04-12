from django.contrib.auth.models import AnonymousUser
from django.db.models import Max
from django.forms import model_to_dict
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

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


