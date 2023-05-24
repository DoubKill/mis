from django.urls import include, path
from rest_framework.routers import DefaultRouter

from projects.views import ProblemViewSet, UploadResourceViewSet, ProblemAnalysisView

router = DefaultRouter()

# 资源上传
router.register(r'resource-upload', UploadResourceViewSet)

# 项目问题汇总
router.register(r'problem', ProblemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('problem-analysis/', ProblemAnalysisView.as_view()),  # 项目问题分析图表
]
