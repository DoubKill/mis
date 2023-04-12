from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, MaterialDisplayViewSet

router = DefaultRouter()

# 物料信息查询
router.register(r'material', MaterialViewSet)

# 物料信息显示设定
router.register(r'material-display', MaterialDisplayViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
