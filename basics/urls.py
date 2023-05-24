from django.urls import include, path
from rest_framework.routers import DefaultRouter

from basics.views import CommonCodeView, GlobalCodeViewSet, GlobalCodeTypeViewSet

router = DefaultRouter()

# 公共代码类型
router.register(r'global-types', GlobalCodeTypeViewSet)

# 公共代码
router.register(r'global-codes', GlobalCodeViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('common-code/', CommonCodeView.as_view()),  # 获取默认的code
]
