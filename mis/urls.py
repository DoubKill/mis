"""mis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.documentation import include_docs_urls

from mis import settings
from basics.views import index

schema_view = get_schema_view(
    openapi.Info(
        title="MES-API",
        default_version='v1.0',
        description="MES接口文档",
        terms_of_service="#",
        contact=openapi.Contact(email="demo"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('api/v1/user/', include('user.urls')),
    path('api/v1/basics/', include('basics.urls')),
    path('api/v1/materials/', include('materials.urls')),
    path('api/v1/projects/', include('projects.urls')),
    path('admin/', admin.site.urls),
    # path('docs/', include_docs_urls(title="MCS系统文档", description="MCS系统文档")),
    # path('api-auth/', include('rest_framework.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path('docs/', include_docs_urls(title="MCS系统文档", description="MCS系统文档")),
        path('api-auth/', include('rest_framework.urls')),
        path('', index, name='index')
    ]
