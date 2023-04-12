# Create your views here.
import pandas as pd
import numpy as np
from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from materials.filters import MaterialFilter
from materials.models import Material, MaterialSetting
from materials.serializers import MaterialSerializer, MaterialDisplaySerializer
from mis.derorators import api_recorder


@method_decorator([api_recorder], name="dispatch")
class MaterialViewSet(ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = MaterialFilter
    filter_backends = (DjangoFilterBackend,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 选中返回的列: 默认返回序号、日期、币种、主计量单位、数量、含税单价、单价、金额、税率、价税合计、累计出口数量
        material_set = MaterialSetting.objects.order_by('id').last()
        if not material_set:
            display_columns = ['seq', 'f_date', 'currency', 'unit', 'quantity', 'tax_unit_price', 'unit_price', 'amount',
                               'total_value_tax', 'cumulative_export_quantity']
        else:
            display_columns = material_set.display_columns.split(',')

        page = self.paginate_queryset(queryset)
        if page is not None:
            data = self.get_serializer(page, many=True).data
            response = self.get_paginated_response(data)
            return Response({**response.data, 'display_columns': display_columns})

        data = self.get_serializer(queryset, many=True).data
        return Response({'results': data, 'display_columns': display_columns})

    @atomic
    def create(self, request, *args, **kwargs):
        import_excel = request.FILES.get('file', None)
        if not import_excel:
            raise ValidationError('文件不可为空!')
        df = pd.read_excel(import_excel)
        if df.empty:
            raise ValidationError('文件内容为空!')
        # 已经存在的seq
        exist_seqs = set(Material.objects.values_list('seq', flat=True))
        # 删除已经在exist_seqs中的seq
        df = df[~df['序号'].isin(exist_seqs)]
        # 替换NAN为None
        handle_df = df.replace({np.nan: None})
        # 将dataframe转换为字典
        data = handle_df.to_dict(orient='records')
        create_data = []
        for item in data:
            s_data = {'seq': item.get('序号', None), 'choice': item.get('选择', None), 'business_type': item.get('业务类型', None),
                      'order_id': item.get('订单编号', None), 'f_date': item.get('日期').date() if item.get('日期') else None,
                      'department': item.get('部门', None), 'salesman': item.get('业务员', None), 'currency': item.get('币种', None),
                      'inventory_code': item.get('存货编码', None), 'inventory_name': item.get('存货名称', None), 'supplier': item.get('供应商', None),
                      'specification': item.get('规格型号', None), 'unit': item.get('单位', None), 'quantity': item.get('数量', None),
                      'tax_unit_price': item.get('含税单价', None), 'unit_price': item.get('单价', None), 'amount': item.get('金额', None),
                      'tax_rate': item.get('税率', None), 'total_value_tax': item.get('价税合计', None), 'pay_terms': item.get('付款条件', None),
                      'cumulative_export_quantity': item.get('累计出口数量', None), 'project_code': item.get('项目编码', None),
                      'project_name': item.get('项目名称', None), 'documenter': item.get('制单人', None), 'closers': item.get('行关闭人', None),
                      'requirement_desc': item.get('需求说明', None), 'unbilled': item.get('未开票数量', None), 'billing_status': item.get('开票状态', None),
                      'plan_arrive_date': item.get('计划到货日期').date() if item.get('计划到货日期') else None, 'cumulative_billed': item.get('累计开票数量', None)}
            create_data.append(s_data)
        if not create_data:
            raise ValidationError('未找到可导入的有效数据!')
        serializer = self.get_serializer(data=create_data, many=True)
        if not serializer.is_valid():
            raise ValidationError('导入数据有误，请检查后重试!')
        self.perform_create(serializer)
        return Response(serializer.data)


@method_decorator([api_recorder], name="dispatch")
class MaterialDisplayViewSet(ModelViewSet):
    queryset = MaterialSetting.objects.all()
    serializer_class = MaterialDisplaySerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
