from django.db.models import Max, ProtectedError
from django.db.transaction import atomic
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from basics.filters import GlobalCodeTypeFilter, GlobalCodeFilter
from basics.models import GlobalCodeType, GlobalCode
from basics.serializers import GlobalCodeTypeSerializer, GlobalCodeSerializer
from mis.common_code import CommonBatchDestroyView, CommonExportListMixin, CommonDeleteMixin
from mis.derorators import api_recorder
from mis.paginations import SinglePageNumberPagination
from user.models import GroupExtension


def index(request):
    request.META["CSRF_COOKIE_USED"] = True
    return render(request, 'index.html')


@method_decorator([api_recorder], name="dispatch")
class CommonCodeView(APIView):

    def get(self, request):
        code = self.request.query_params.get('code')
        if code == '1':
            prefix, model_name = ['T', GlobalCodeType]
            max_code = model_name.objects.filter(
                type_no__startswith=prefix).aggregate(max_code=Max('type_no'))['max_code']
        elif code == '2':
            prefix, model_name = ['C', GlobalCode]
            max_code = model_name.objects.filter(
                global_no__startswith=prefix).aggregate(max_code=Max('global_no'))['max_code']
        elif code == '3':
            prefix, model_name = ['R', GroupExtension]
            max_code = model_name.objects.filter(
                group_code__startswith=prefix).aggregate(max_code=Max('group_code'))['max_code']
        else:
            raise ValidationError('参数错误')
        try:
            if not max_code:
                default_code = f'{prefix}00001'
            else:
                s = len(prefix)
                default_code = '{}{:05}'.format(prefix, int(max_code[s:]) + 1)
        except Exception:
            raise ValidationError('解析自增公共编码异常')
        return Response(data={'results': default_code})


@method_decorator([api_recorder], name="dispatch")
class GlobalCodeTypeViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        公共代码类型列表
    create:
        创建公共代码类型
    update:
        修改公共代码类型
    destroy:
        删除公共代码类型
    """
    queryset = GlobalCodeType.objects.filter(delete_flag=False).order_by("id")
    serializer_class = GlobalCodeTypeSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = GlobalCodeTypeFilter


@method_decorator([api_recorder], name="dispatch")  # 本来是删除，现在改为是启用就改为禁用 是禁用就改为启用
class GlobalCodeViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        公共代码列表
    create:
        创建公共代码
    update:
        修改公共代码
    destroy:
        删除公共代码
    """
    queryset = GlobalCode.objects.filter(delete_flag=False, global_type__use_flag=1).order_by("id")
    serializer_class = GlobalCodeSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = SinglePageNumberPagination
    filter_class = GlobalCodeFilter

    def get_permissions(self):
        if self.action == 'list':
            return ()
        else:
            return (IsAuthenticated(),)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        clock_type = self.request.query_params.get('clock_type', '密炼')  # 增加标志[获取称量、密炼当天排班信息]
        if self.request.query_params.get('all'):
            data = queryset.filter(use_flag=1, global_type__use_flag=1).values('id', 'global_no', 'global_name',
                                                                               'global_type__type_name')
            return Response({'results': data})
        else:
            return super().list(request, *args, **kwargs)

