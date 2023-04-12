from django.urls import include, path
from rest_framework.routers import DefaultRouter

from user.views import LoginView, ResetPassword, UserViewSet, GroupExtensionViewSet, DepartmentViewSet, GroupPermissions, UserOperationLogViewSet

router = DefaultRouter()

# 用户操作
router.register(r'personnels', UserViewSet)

# 角色
router.register(r'group_extension', GroupExtensionViewSet)

# 部门
router.register(r'department', DepartmentViewSet)

# 操作记录
router.register(r'user-operation-log', UserOperationLogViewSet)

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('reset-password/', ResetPassword.as_view()),
    path('group-permissions/', GroupPermissions.as_view()),
    path('', include(router.urls)),
]
