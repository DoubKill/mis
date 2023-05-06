# Create your views here.
import pandas as pd
import numpy as np
from datetime import datetime
from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from basics.models import GlobalCode
from materials.filters import MaterialFilter
from materials.models import Material, MaterialSetting
from materials.serializers import MaterialSerializer, MaterialDisplaySerializer
from mis.common_code import gen_template_response, operate_record
from mis.derorators import api_recorder


@method_decorator([api_recorder], name="dispatch")
class MaterialViewSet(ModelViewSet):
    queryset = Material.objects.all().order_by('id')
    serializer_class = MaterialSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = MaterialFilter
    filter_backends = (DjangoFilterBackend,)
    SHEET_NAME = '价格查询'
    TEMPLATE_FILE = 'xlsx_template/example.xlsx'
    EXPORT_FIELDS_DICT = {
        '存货编码': 'inventory_code',
        '存货名称': 'inventory_name',
        '规格型号': 'specification',
        '原币单价': 'unit_price'
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 数据导入日期
        l_record = self.get_queryset().last()
        export_date = '' if not l_record else l_record.created_time.strftime('%Y/%m/%d')
        export_user = '' if not l_record else l_record.created_user.username
        # 选中返回的列: 默认返回序号、日期、币种、主计量单位、数量、含税单价、单价、金额、税率、价税合计、累计出口数量
        material_set = MaterialSetting.objects.order_by('id').last()
        if not material_set:
            display_columns = ['seq', 'f_date', 'currency', 'inventory_code', 'inventory_name', 'specification',
                               'unit', 'quantity', 'tax_unit_price', 'unit_price', 'amount', 'total_value_tax',
                               'cumulative_export_quantity', 'project_code', 'project_name']
        else:
            display_columns = material_set.display_columns.split(',')

        page = self.paginate_queryset(queryset)
        if page is not None:
            data = self.get_serializer(page, many=True).data
            response = self.get_paginated_response(data)
            return Response({**response.data, 'display_columns': display_columns, 'export_date': export_date, 'export_user': export_user})

        data = self.get_serializer(queryset, many=True).data
        return Response({'results': data, 'display_columns': display_columns, 'export_date': export_date, 'export_user': export_user})

    @action(methods=['post'], detail=False, url_path='multi-query', url_name='multi_query')
    def multi_query(self, request):
        query_file = request.FILES.get('query_file', None)  # 存货编码、存货名称、规格型号、单价
        if not query_file:
            raise ValidationError('查询文件不可为空!')
        df = pd.read_excel(query_file)
        if df.empty:
            raise ValidationError('查询文件内容为空!')
        # 获取默认排序
        material_set = GlobalCode.objects.filter(delete_flag=False, global_type__delete_flag=False, global_type__type_name='物料信息列顺序').order_by('seq')
        g_set = list(material_set.values_list('global_name', flat=True))
        # 存在不同列
        if set(df.columns) - set(g_set):
            raise ValidationError('存在与公用设置不匹配的列!')
        # 全部导入
        filter_df = df.dropna(how='all')
        if filter_df.empty:
            raise ValidationError('未找到有效数据!')
        # set_df 数量不能大于相应数量
        limit_set = GlobalCode.objects.filter(delete_flag=False, global_type__delete_flag=False, global_type__type_name='批量查询限制').last()
        try:
            limit_num = 20 if not limit_set else int(limit_set.global_name)
        except:
            raise ValidationError('批量查询限制设置错误!')
        if len(filter_df) > limit_num:
            raise ValidationError(f'一次查询不能超过{limit_num}条数据!')
        # 替换NAN为None
        handle_df = filter_df.replace({np.nan: None})
        # 所有查询条件
        data = handle_df.to_dict(orient='records')
        # 查询结果
        results, code_list, name_list, specification_list = [], [], [], []
        for item in data:
            inventory_code, inventory_name, specification, unit_price = item.get('存货编码'), item.get('存货名称'), item.get('规格型号'), item.get('原币单价')
            inventory_code = '' if not inventory_code else (inventory_code.strip() if isinstance(inventory_code, str) else str(inventory_code).rstrip('.0'))
            inventory_name = '' if not inventory_name else (inventory_name.strip() if isinstance(inventory_name, str) else str(inventory_name).rstrip('.0'))
            specification = '' if not specification else (specification.strip() if isinstance(specification, str) else str(specification).rstrip('.0'))
            unit_price = '' if not unit_price else unit_price
            filter_kwargs = {}
            if all([inventory_code, inventory_name, specification]):
                filter_kwargs = {'inventory_code': inventory_code, 'inventory_name': inventory_name, 'specification': specification}
                code_list.append(inventory_code)
            else:
                if inventory_code:
                    filter_kwargs['inventory_code'] = inventory_code
                    code_list.append(inventory_code)
                if inventory_name:
                    filter_kwargs['inventory_name'] = inventory_name
                    name_list.append(inventory_name)
                if specification:
                    filter_kwargs['specification'] = specification
                    specification_list.append(specification)
            instance = Material.objects.filter(**filter_kwargs).order_by('f_date', 'id').last()
            if instance:
                _s_data = {'inventory_code': instance.inventory_code, 'inventory_name': instance.inventory_name,
                           'specification': instance.specification, 'unit_price': instance.unit_price}
            else:
                _s_data = {'inventory_code': inventory_code, 'inventory_name': inventory_name,
                           'specification': specification, 'unit_price': unit_price}
            results.append(_s_data)
        # 记录履历
        code_str = ','.join(code_list)
        name_str = ','.join(name_list)
        specification_str = ','.join(specification_list)
        operate_record({'operator_type': '批量查询', 'operator_reason': '批量查询物料信息查询', 'operator_user': self.request.user.username,
                        'operation_detail': f"批量查询{len(results)}条物料编码-编码:{code_str}, 名称: {name_str}, 规格: {specification_str}"})
        file_name = f'批量查询单价{datetime.now().strftime("%Y-%m-%d %H_%M_%S")}.xlsx'
        return gen_template_response(self.EXPORT_FIELDS_DICT, results, file_name, self.SHEET_NAME, self.TEMPLATE_FILE)

    @atomic
    def create(self, request, *args, **kwargs):
        import_excel = request.FILES.get('file', None)
        ignore_flag = request.data.get('ignore_flag', False)
        if not import_excel:
            raise ValidationError('文件不可为空!')
        df = pd.read_excel(import_excel)
        if df.empty:
            raise ValidationError('文件内容为空!')
        # 必须导入的项目
        must_set = ['存货编码', '存货名称', '规格型号', '原币含税单价', '原币单价']
        if set(df.columns) & set(must_set) != set(must_set):
            raise ValidationError('导入数据必须包含存货编码、存货名称、规格型号、原币含税单价、原币单价!')
        # 获取默认排序
        g_set = list(GlobalCode.objects.filter(delete_flag=False, global_type__delete_flag=False, global_type__type_name='物料信息列顺序').order_by('seq').values_list('global_name', flat=True))
        # 存在不同列
        if set(df.columns) - set(g_set):
            raise ValidationError('存在与公用设置不匹配的列!')
        # 筛选字段
        df = df[g_set]
        # 全部导入
        filter_df = df[~df['选择'].isin(['小计', '合计'])].dropna(how='all')
        if filter_df.empty:
            raise ValidationError('未找到有效数据!')
        # 校验filter_df中必填字段是否存在为空的情况
        if not ignore_flag and filter_df[must_set].isna().any().any():
            return Response({'msg': '导入数据必须包含存货编码、存货名称、规格型号、原币含税单价、原币单价!', 'ignore_flag': False})
        self.get_queryset().delete()
        # 替换NAN为None
        handle_df = filter_df.replace({np.nan: None})
        # 将dataframe转换为字典
        data = handle_df.to_dict(orient='records')
        create_data = []
        for item in data:
            inventory_code = item.get('存货编码', None)
            if inventory_code:
                inventory_code = str(int(inventory_code))
            s_data = {'seq': item.get('序号', None), 'choice': item.get('选择', None), 'business_type': item.get('业务类型', None),
                      'order_id': item.get('订单编号', None), 'f_date': item.get('日期').date() if item.get('日期') else None,
                      'department': item.get('部门', None), 'salesman': item.get('业务员', None), 'currency': item.get('币种', None),
                      'inventory_code': inventory_code, 'inventory_name': item.get('存货名称', None), 'supplier': item.get('供应商', None),
                      'specification': item.get('规格型号', None), 'unit': item.get('主计量', None), 'quantity': item.get('数量', None),
                      'tax_unit_price': item.get('原币含税单价', None), 'unit_price': item.get('原币单价', None), 'amount': item.get('原币金额', None),
                      'tax_rate': item.get('税率', None), 'total_value_tax': item.get('原币价税合计', None), 'pay_terms': item.get('付款条件', None),
                      'cumulative_export_quantity': item.get('累计出口数量', None), 'project_code': item.get('项目编码', None),
                      'project_name': item.get('项目名称', None), 'documenter': item.get('制单人', None), 'closers': item.get('行关闭人', None),
                      'requirement_desc': item.get('需求分类代码说明', None), 'unbilled': item.get('未开票量', None), 'billing_status': item.get('开票状态', None),
                      'plan_arrive_date': item.get('计划到货日期').date() if item.get('计划到货日期') else None, 'cumulative_billed': item.get('累计开票量', None),
                      'tax_amount': item.get('原币税额', None), 'created_user': request.user}
            create_data.append(Material(**s_data))
        if not create_data:
            raise ValidationError('未找到可导入的有效数据!')
        Material.objects.bulk_create(create_data)
        return Response(f'导入{len(create_data)}条数据成功!')


@method_decorator([api_recorder], name="dispatch")
class MaterialDisplayViewSet(ModelViewSet):
    queryset = MaterialSetting.objects.all()
    serializer_class = MaterialDisplaySerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)