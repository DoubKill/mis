import logging
import pandas as pd
from datetime import datetime
from django.db.models import Max, Count, F
from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from basics.models import GlobalCode
from mis.common_code import gen_excels_response
from mis.derorators import api_recorder
from projects.filters import ProblemFilter
from projects.models import ProjectSummary, UploadResource
from projects.serializers import ProblemSerializer, UploadResourceSerializer, ProblemUpdateSerializer

# Create your views here.
error_log = logging.getLogger('error_log')


@method_decorator([api_recorder], name='dispatch')
class UploadResourceViewSet(ModelViewSet):
    """
    create:上传图片
    """
    queryset = UploadResource.objects.all()
    serializer_class = UploadResourceSerializer
    filter_backends = (DjangoFilterBackend,)


@method_decorator([api_recorder], name="dispatch")
class ProblemViewSet(ModelViewSet):
    queryset = ProjectSummary.objects.filter(delete_flag=False)
    serializer_class = ProblemSerializer
    permission_classes = (IsAuthenticated, )
    filter_class = ProblemFilter
    filter_backends = (DjangoFilterBackend, )

    def get_serializer_context(self):
        all_departments = list(GlobalCode.objects.filter(use_flag=True, global_type__use_flag=True, global_type__type_name='项目问题部门').values_list('global_name', flat=True))
        all_status = list(GlobalCode.objects.filter(use_flag=True, global_type__use_flag=True, global_type__type_name='项目问题状态').values_list('global_name', flat=True))
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'all_status': all_status,
            'all_departments': all_departments
        }

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ProblemUpdateSerializer
        return ProblemSerializer

    def get_queryset(self):
        max_times = self.queryset.aggregate(max_times=Max('times'))['max_times']
        return self.queryset.filter(times=max_times).order_by('project_name', 'seq', 'id')

    def list(self, request, *args, **kwargs):
        """列表页"""
        export = self.request.query_params.get('export')
        queryset = self.filter_queryset(self.get_queryset())
        if export:
            if not queryset:
                raise ValidationError('没有数据可以导出')
            export_data = {}
            serializer_data = self.get_serializer(queryset, many=True).data
            for item in serializer_data:
                project_name = item['project_name']
                export_data.setdefault(project_name, []).append(item)
            file_name = '项目问题汇总.xlsx'
            columns_set = dict(GlobalCode.objects.filter(global_type__type_name='项目问题导入列', global_type__use_flag=True, use_flag=True).values_list('global_name', 'description'))
            return gen_excels_response(columns_set, export_data, file_name)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @atomic
    @action(methods=['post'], detail=False, url_path='import-excel', url_name='import_excel')
    def import_excel(self, request, *args, **kwargs):
        """导入excel, 包含多个项目的sheet"""
        import_file = self.request.FILES.get('import_file')
        if not import_file:
            raise ValidationError('导入文件不能为空')
        # 项目导入列
        columns_set = dict(GlobalCode.objects.filter(global_type__type_name='项目问题导入列', global_type__use_flag=True, use_flag=True).values_list('description', 'global_name'))
        if not columns_set:
            raise ValidationError('请先配置项目问题导入列')
        created_data = []
        # 最大次数
        max_times = ProjectSummary.objects.filter(delete_flag=False).aggregate(max_times=Max('times'))['max_times']
        times = 1 if not max_times else (max_times + 1)
        excel_datas = pd.read_excel(import_file, sheet_name=None)
        for sheet_name, sheet_data in excel_datas.items():
            if not sheet_name:
                continue
            try:
                _sheet_data = sheet_data.where(sheet_data.notnull(), None)
                problem_title = _sheet_data.columns[0]
                # 修改列名
                _sheet_data.columns = _sheet_data.iloc[1]
                h_data = _sheet_data.iloc[2:]
                if None in _sheet_data.columns:
                    real_data = h_data.drop(columns=[None]).to_dict(orient='records')
                else:
                    real_data = h_data.to_dict(orient='records')
                for _data in real_data:
                    seq = _data.get(columns_set.get('seq'))
                    raise_date = _data.get(columns_set.get('raise_date'))
                    unusual_item = _data.get(columns_set.get('unusual_item'))
                    solution = _data.get(columns_set.get('solution'))
                    department = _data.get(columns_set.get('department'))
                    hope_date = _data.get(columns_set.get('hope_date'))
                    plan_date = _data.get(columns_set.get('plan_date'))
                    actual_date = _data.get(columns_set.get('actual_date'))
                    status = _data.get(columns_set.get('status'))
                    remark = _data.get(columns_set.get('remark'))
                    if not any([raise_date, unusual_item, solution, department, hope_date, plan_date, actual_date, status]):
                        continue
                    h_raise_date = raise_date if not isinstance(raise_date, datetime) else raise_date.strftime('%Y-%m-%d')
                    h_plan_date = plan_date if not isinstance(plan_date, datetime) else plan_date.strftime('%Y-%m-%d')
                    h_hope_date = hope_date if not isinstance(hope_date, datetime) else hope_date.strftime('%Y-%m-%d')
                    h_actual_date = actual_date if not isinstance(actual_date, datetime) else actual_date.strftime('%Y-%m-%d')
                    _temp = {'seq': seq, 'raise_date': h_raise_date, 'unusual_item': unusual_item, 'solution': solution, 'department': department,
                             'hope_date': h_hope_date, 'plan_date': h_plan_date, 'status': status, 'remark': remark, 'actual_date': h_actual_date,
                             'problem_title': problem_title, 'project_name': sheet_name, 'times': times}
                    created_data.append(_temp)
            except Exception as e:
                error_log.error(f'导入失败, sheet: {sheet_name}, reason: {e.args[0]}')
                raise ValidationError(f'导入时出现异常!')
        if created_data:
            serializer = self.get_serializer(data=created_data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            raise ValidationError('导入失败, 请检查所有sheet的格式！')
        return Response('导入成功!')


@method_decorator([api_recorder], name="dispatch")
class ProblemAnalysisView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """问题分析图表"""
        analysis_type = request.query_params.get('analysis_type', '部门')  # 状态、部门
        if not analysis_type:
            raise ValidationError('请选择分析纬度!')
        keyword = 'status' if analysis_type == '状态' else 'department'
        max_times = ProjectSummary.objects.filter(delete_flag=False).aggregate(max_times=Max('times'))['max_times']
        data = ProjectSummary.objects.filter(times=max_times).values(keyword).annotate(name=F(keyword), value=Count('id')).values('name', 'value').order_by('-value')
        # 比例
        total = sum([i.get('value') for i in data])
        for i in data:
            i['rate'] = round(i.get('value') / total * 100, 2) if total else 0
        return Response(list(data))
