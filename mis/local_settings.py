import os
import datetime

from mis.settings import BASE_DIR, INSTALLED_APPS

# X_FRAME_OPTIONS = 'ALLOWALL url'

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=3),
    'JWT_ALLOW_REFRESH': True,
}

# drf通用配置
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',  # 文档
    'DEFAULT_PERMISSION_CLASS': ('rest_framework.permissions.IsAuthenticated',),  # 权限
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),  # 认证
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),  # 过滤
    'DEFAULT_PAGINATION_CLASS': 'mis.paginations.DefaultPageNumberPagination',  # 分页
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'prompt': '1/s',
    }
}

REST_FRAMEWORK_EXTENSIONS = {
    # 缓存时间(1小时)
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 10,
    # 缓存到哪里 (caches中配置的default)
    'DEFAULT_USE_CACHE': 'default',
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     },
# }


DATABASES = {
    'default': {
        'ENGINE': os.getenv('MES_ENGINE', 'django.db.backends.mysql'),  # 数据库引擎
        'NAME': os.getenv('MES_DATABASE_NAME', 'test'),  # 数据库名称
        'USER': os.getenv('MES_DATABASE_USERNAME', 'root'),  # 用户名
        'PASSWORD': os.getenv('MES_DATABASE_PASSWORD', '123456'),  # 密码
        'HOST': os.getenv('MES_DATABASE_HOSTNAME', '10.10.120.55'),  # HOST
        'PORT': os.getenv('MES_MONOCLE_API_PORT', '3306'),  # 端口
        }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, '../MCS/dist')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, 'static'),# 项目默认会有的路径，如果你部署的不仅是前端打包的静态文件，项目目录static文件下还有其他文件，最好不要删
    os.path.join(BASE_DIR, "../MCS/dist/static"),  # 加上这条
]

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, "media/"))
MEDIA_URL = '/media/'
