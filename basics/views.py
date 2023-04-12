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

from basics.models import GlobalCodeType, GlobalCode
from mis.common_code import CommonBatchDestroyView, CommonExportListMixin
from mis.derorators import api_recorder
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

