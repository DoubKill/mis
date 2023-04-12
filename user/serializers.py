import json

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate

from basics.serializers import BaseModelSerializer
from mis.settings import COMMON_READ_ONLY_FIELDS
from user.models import User, Department, GroupExtension, UserOperationLog

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class UserLoginSerializer(JSONWebTokenSerializer):

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError('该账号已被停用！')

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                raise serializers.ValidationError('用户名或密码错误！')
        else:
            raise serializers.ValidationError('请输入用户名和密码')


class UserResetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(max_length=128, help_text='新密码')
    old_password = serializers.CharField(max_length=128, help_text='原密码')

    class Meta:
        model = User
        fields = ('new_password', 'old_password')


class UserSerializer(BaseModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    department_name = serializers.CharField(source="department.name", default="", read_only=True)
    group_names = serializers.SerializerMethodField(read_only=True)
    active_flag = serializers.SerializerMethodField(read_only=True)

    def get_active_flag(self, obj):
        return 'Y' if obj.is_active else 'N'

    def get_group_names(self, obj):
        return '/'.join(list(obj.group_extensions.values_list('name', flat=True)))

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        instance.pop('password')
        return instance

    def create(self, validated_data):
        password = validated_data.get('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        exclude = ('user_permissions', 'groups')
        extra_kwargs = {
            'group_extensions': {
                'required': False
            },
            'is_superuser': {
                'read_only': True
            }
        }


class UserRetrieveSerializer(UserSerializer):
    factory_id = serializers.SerializerMethodField(read_only=True)

    def get_factory_id(self, obj):
        ret = []
        department = obj.department
        if not department:
            return None
        while department:
            ret.append(department.id)
            department = department.parent_section
        return ret[-2]


class UserImportSerializer(BaseModelSerializer):
    username = serializers.CharField(max_length=150)
    department = serializers.CharField(max_length=512, allow_null=True, allow_blank=True)
    group_extensions = serializers.CharField(max_length=512, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        department_name = attrs.pop('department', None)
        permissions = attrs.pop('group_extensions', None)
        if department_name:
            department = Department.objects.filter(name=department_name).first()
            if not department:
                raise serializers.ValidationError('未找到该部门：{}'.format(department_name))
            attrs['department'] = department
        if permissions:
            permissions = permissions.split('/')
            ps = []
            for permission in permissions:
                p = GroupExtension.objects.filter(name=permission).first()
                if not p:
                    raise serializers.ValidationError('未找到该角色：{}'.format(permission))
                ps.append(p.id)
                attrs['group_extensions'] = ps
        return attrs

    def create(self, validated_data):
        password = validated_data.get('password')
        try:
            user = super().create(validated_data)
        except Exception:
            raise serializers.ValidationError('该用户名已存在：{}'.format(validated_data['username']))
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'password', 'department', 'group_extensions', 'is_active', 'delete_flag')


class UserUpdateSerializer(BaseModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    phone_number = serializers.ReadOnlyField()
    id_card_num = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        instance.pop('password')
        return instance

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(validated_data['password']) if validated_data.get(
            'password') else instance.password
        return super(UserUpdateSerializer, self).update(instance, validated_data)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'group_extensions': {
                'allow_empty': True
            }
        }


class UserOperationLogSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField(read_only=True)

    def get_date(self, obj):
        return obj.create_time.strftime('%Y-%m-%d')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        operation_desc = json.dumps(instance.operation_desc, ensure_ascii=False) if instance.operation_desc else ""
        res['operation_desc'] = operation_desc
        return res

    class Meta:
        model = UserOperationLog
        fields = '__all__'
        read_only_fields = ('create_time', )


class GroupExtensionSerializer(BaseModelSerializer):
    """角色组扩展序列化器"""

    class Meta:
        model = GroupExtension
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class DepartmentSerializer(BaseModelSerializer):
    name = serializers.CharField(max_length=40, validators=[
        UniqueValidator(queryset=Department.objects.all(), message='该部门已存在')])
    users = serializers.SerializerMethodField()
    in_charge_username = serializers.CharField(source='in_charge_user.username', read_only=True)

    def get_users(self, obj):
        temp_set = obj.section_users.filter(delete_flag=False).values_list("username", flat=True)
        return list(temp_set)

    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS
