from django.urls import include, path
from rest_framework.routers import DefaultRouter

from basics.views import CommonCodeView

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('common-code/', CommonCodeView.as_view()),  # 获取默认的code
]
