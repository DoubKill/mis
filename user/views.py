
# Create your views here.
from django.db.models import F
from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_jwt.views import ObtainJSONWebToken

from mis.common_code import CommonExportListMixin, CommonBatchDestroyView, get_cur_sheet, get_sheet_data
from mis.derorators import api_recorder
from user.filters import UserFilter, GroupExtensionFilter, DepartmentFilter, UserOperationLogFilter
from user.models import User, Department, GroupExtension, Permissions, UserOperationLog
from user.serializers import UserLoginSerializer, UserResetPasswordSerializer, UserSerializer, UserRetrieveSerializer, UserImportSerializer, \
    UserUpdateSerializer, GroupExtensionSerializer, DepartmentSerializer, UserOperationLogSerializer
from user.utils import PasswordRSAer


@method_decorator([api_recorder], name="dispatch")
class LoginView(ObtainJSONWebToken):
    """
        用户登录
    """
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        req_data = request.data
        password = req_data.get('password')
        if not password:
            raise ValidationError('请输入密码！')
        crypt_er = PasswordRSAer()
        try:
            req_data['password'] = crypt_er.rsa_decrypt_password(password)
        except Exception:
            raise ValidationError('数据错误！')
        serializer = self.get_serializer(data=req_data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            permissions = user.permissions_list
            if not permissions:
                raise ValidationError('账户没有权限, 联系管理员!')
            token = serializer.object.get('token')
            return Response({'section': user.department.name if user.department else None,
                             'id_card_num': user.id_card_num,
                             "username": user.username,
                             'id': user.id,
                             "token": token,
                             "permissions": permissions,
                             'is_superuser': user.is_superuser})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator([api_recorder], name="dispatch")
class ResetPassword(GenericAPIView):
    """
        用户修改密码
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserResetPasswordSerializer

    def post(self, request):
        user = self.request.user
        req_data = request.data
        new_password = req_data.get('new_password')
        old_password = req_data.get('old_password')
        if not all([new_password, old_password]):
            raise ValidationError('请输入密码！')
        crypt_er = PasswordRSAer()
        try:
            req_data['new_password'] = crypt_er.rsa_decrypt_password(new_password)
            req_data['old_password'] = crypt_er.rsa_decrypt_password(old_password)
        except Exception:
            raise ValidationError('数据错误！')
        s = self.serializer_class(data=req_data)
        s.is_valid(raise_exception=True)
        if not user.check_password(s.validated_data['old_password']):
            raise ValidationError('原密码错误！')
        user.set_password(s.validated_data['new_password'])
        user.save()
        return Response('修改成功')


@method_decorator([api_recorder], name="dispatch")
class UserViewSet(CommonExportListMixin, CommonBatchDestroyView, ModelViewSet):
    """
    list:
        用户列表
    create:
        创建用户
    update:
        修改用户
    destroy:
        账号停用和启用
    """
    queryset = User.objects.filter(delete_flag=False, is_superuser=False).order_by('id').prefetch_related('group_extensions')
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = UserFilter
    ordering_fields = ['last_updated_time']
    EXPORT_FIELDS_DICT = {
        '用户名': 'username',
        '部门': 'department_name',
        '创建人': 'created_username',
        '创建日期': 'created_time',
        '修改人': 'last_update_username',
        '修改日期': 'last_updated_time',
        '角色': 'group_names'}
    FILE_NAME = '用户列表.xlsx'
    VALUES_FIELDS = ['id', 'username', 'is_active', 'department__name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserRetrieveSerializer
        elif self.action in ['list', 'create']:
            return UserSerializer
        else:
            return UserUpdateSerializer

    @atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated, ], url_path='del-user',
            url_name='del_user')
    def del_user(self, request, *args, **kwargs):
        # 账号停用和启用
        obj_ids = self.request.data.get('obj_ids')
        for i in obj_ids:
            try:
                instance = self.get_queryset().get(id=i)
            except Exception as e:
                raise ValidationError('object does not exists!')
            if instance.is_active:
                instance.is_active = 0
            else:
                instance.is_active = 1
            instance.last_updated_user = self.request.user
            instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated, ], url_path='import_xlsx',
            url_name='import_xlsx')
    def import_xlx(self, request):
        excel_file = request.FILES.get('file', None)
        if not excel_file:
            raise ValidationError('文件不可为空！')
        cur_sheet = get_cur_sheet(excel_file)
        if cur_sheet.ncols != 4:
            raise ValidationError('导入文件数据错误！')
        data = get_sheet_data(cur_sheet, start_row=1)
        user_list = []
        for item in data:
            user_data = {
                "username": item[0],
                "password": item[1],
                "department": item[2],
                "group_extensions": item[3],
                "is_active": True,
                "delete_flag": False
            }
            user_list.append(user_data)
        s = UserImportSerializer(data=user_list, many=True, context={'request': self.request})
        if not s.is_valid():
            for i in s.errors:
                if i:
                    raise ValidationError(list(i.values())[0])
        validated_data = s.validated_data
        username_list = [item['username'] for item in validated_data]
        if len(username_list) != len(set(username_list)):
            raise ValidationError('导入数据中存在相同的用户名，请修改后重试！')
        s.save()
        return Response('ok')


@method_decorator([api_recorder], name="dispatch")
class GroupExtensionViewSet(CommonExportListMixin, ModelViewSet):
    """
    list:
        角色列表,xxx?all=1查询所有
    create:
        创建角色
    update:
        修改角色
    destroy:
        删除角色
    """
    queryset = GroupExtension.objects.filter(
        delete_flag=False).prefetch_related('permissions').order_by('-created_time')
    serializer_class = GroupExtensionSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = GroupExtensionFilter
    VALUES_FIELDS = ['id', 'name']

    def get_permissions(self):
        if self.request.query_params.get('all'):
            return ()
        else:
            return (IsAuthenticated(),)

    @atomic()
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated], url_path='batch-destroy', url_name='batch-destroy')
    def batch_destroy(self, request):
        obj_ids = self.request.data.get('obj_ids')
        groups = self.get_queryset().filter(id__in=obj_ids, group_users__isnull=False)
        if groups:
            raise ValidationError('存在被使用的角色, 请解除关联后删除！')
        self.get_queryset().filter(id__in=obj_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        # 账号停用和启用
        instance = self.get_object()
        if instance.is_used:
            instance.is_used = 0
        else:
            instance.is_used = 1
        instance.last_updated_user = self.request.user
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator([api_recorder], name="dispatch")
class GroupPermissions(APIView):
    """获取权限表格数据"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        ret = []
        parent_permissions = Permissions.objects.filter(parent__isnull=True)
        for perm in parent_permissions:
            ret.append({'name': perm.name, 'permissions': perm.children_list, 'category_name': perm.category_name})
        return Response(data={'result': ret})


@method_decorator([api_recorder], name="dispatch")
class DepartmentViewSet(CommonExportListMixin, CommonBatchDestroyView, ModelViewSet):
    """
    list:
        部门列表
    create:
        创建部门
    update:
        修改部门
    destroy:
        删除部门
    """
    queryset = Department.objects.order_by('id')
    serializer_class = DepartmentSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = DepartmentFilter

    def list(self, request, *args, **kwargs):
        if self.request.query_params.get("all"):
            data = self.get_queryset().filter(parent_section__isnull=False).values('id', 'name')
            return Response({'results': data})
        if self.request.query_params.get('section_users'):
            department = self.queryset.filter(section_users=self.request.user).first()
            return Response({'section': department.name if department else None})
        if self.request.query_params.get('department_name'):
            # 根据部门获取部门负责人
            name = self.request.query_params.get('department_name')
            department = self.queryset.filter(name=name).first()
            in_charge_user = None
            if department:
                in_charge_user = department.in_charge_user.username if department.in_charge_user else None
            return Response({'in_charge_user': in_charge_user})
        data = []
        index_tree = {}
        for department in Department.objects.order_by('id'):
            in_charge_username = department.in_charge_user.username if department.in_charge_user else ''
            if department.id not in index_tree:
                index_tree[department.id] = dict({'id': department.id,
                                                  'in_charge_user_id': department.in_charge_user_id,
                                                  'in_charge_username': in_charge_username,
                                                  'label': department.name,
                                                  'children': []})

            if not department.parent_section_id:  # 根节点
                data.append(index_tree[department.id])  # 浅拷贝
                continue

            if department.parent_section_id in index_tree:  # 子节点
                if "children" not in index_tree[department.parent_section_id]:
                    index_tree[department.parent_section_id]["children"] = []

                index_tree[department.parent_section_id]["children"].append(index_tree[department.id])
            else:  # 没有节点则加入
                index_tree[department.parent_section_id] = dict(
                    {"id": department.parent_section_id,
                     'in_charge_user_id': department.in_charge_user_id,
                     'in_charge_username': in_charge_username,
                     "label": department.parent_section.name,
                     "children": []})
                index_tree[department.parent_section_id]["children"].append(index_tree[department.id])
        return Response({'results': data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.section_users.filter(delete_flag=False).exists():
            raise ValidationError('操作无效，该部门下存在用户！')
        if instance.children_sections.exists():
            raise ValidationError('操作无效，该部门下存在子部门！')
        return super().destroy(request, *args, **kwargs)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated], url_path='tree',
            url_name='tree')
    def tree(self, request):
        data = []
        index_tree = {}
        for department in Department.objects.all():
            in_charge_username = department.in_charge_user.username if department.in_charge_user else ''
            if department.id not in index_tree:
                index_tree[department.id] = dict(
                    {"section_id": department.id, 'in_charge_username': in_charge_username, "label": department.name,
                     'children': list(User.objects.filter(section=department, is_active=1).values(user_id=F('id'),
                                                                                                  label=F('username')))})

            if not department.parent_section_id:  # 根节点
                data.append(index_tree[department.id])  # 浅拷贝
                continue

            if department.parent_section_id in index_tree:  # 子节点
                if "children" not in index_tree[department.parent_section_id]:
                    index_tree[department.parent_section_id]["children"] = list(User.objects.filter(section=department.parent_section,
                                                                                                    is_active=1).values(user_id=F('id'),
                                                                                                                        label=F('username')))

                index_tree[department.parent_section_id]["children"].append(index_tree[department.id])
            else:  # 没有节点则加入
                index_tree[department.parent_section_id] = dict(
                    {"section_id": department.parent_section_id, 'in_charge_username': in_charge_username,
                     "label": department.parent_section.name, "children": list(User.objects.filter(section=department.parent_section,
                                                                                                   is_active=1).values(user_id=F('id'),
                                                                                                                       label=F('username')))})
                index_tree[department.parent_section_id]["children"].append(index_tree[department.id])
        return Response({'results': data})


@method_decorator([api_recorder], name="dispatch")
class UserOperationLogViewSet(CommonExportListMixin, ModelViewSet):
    queryset = UserOperationLog.objects.order_by('-id')
    serializer_class = UserOperationLogSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (DjangoFilterBackend, )
    filter_class = UserOperationLogFilter
    EXPORT_FIELDS_DICT = {
        '操作人': 'operator_user',
        '操作时间': 'create_time',
        '操作类型': 'operator_type',
        '操作原因': 'operator_reason',
        '操作描述': 'operator_desc'}
    FILE_NAME = '操作履历'


