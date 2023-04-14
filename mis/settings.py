"""
Django settings for mis project.

Generated by 'django-admin startproject' using Django 2.1.15.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import datetime
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gqg9yy_rcmce1&+y9#r#-s-n$q-j+wrw#c=!_0^=&9)u65!hgc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'drf_yasg',
    'django_filters',
    'materials.apps.MaterialsConfig',
    'user.apps.UserConfig',
    'basics.apps.BasicsConfig',
    'django_extensions',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mis.middlewares.DisableCSRF',
]

ROOT_URLCONF = 'mis.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'mis.wsgi.application'

# drf通用配置
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',  # 文档
    # 'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),  # 权限
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ) if DEBUG else ('rest_framework_jwt.authentication.JSONWebTokenAuthentication',),  # 认证
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),  # 过滤
    'DEFAULT_PAGINATION_CLASS': 'mis.paginations.DefaultPageNumberPagination',  # 分页
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

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

# 多数据库读写路由配置
DATABASE_ROUTERS = ['mis.db_route.AppRouter']

LOGGING_DIR = os.environ.get('LOGGING_DIR', os.path.join(BASE_DIR, 'logs'))

# 日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] '
                      '[%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'
        },
        'django_request': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(module)s %(lineno)d %(message)s'
                      ' status_code:%(status_code)d',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'django_db_backends': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(module)s %(lineno)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'django_db_backends': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'django_db_backends'
        },
        'django_request': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'django_request'
        },
        'timedRotatingFile': {
            'level': 'DEBUG',
            'class': 'mis.custom_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'api_log.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'standard',
            'interval': 1,
        },
        'errorFile': {
            'level': 'DEBUG',
            'class': 'mis.custom_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'error.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'standard',
            'interval': 1,
        },
        'syncFile': {
            'level': 'DEBUG',
            'class': 'mis.custom_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'sync.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'standard',
            'interval': 1,
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['django_db_backends'],
            'propagate': True,
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'django.request': {
            'handlers': ['django_request'],
            'level': 'ERROR',
            'propagate': False,
        },
        'api_log': {
            'handlers': ['timedRotatingFile'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'error_log': {
            'handlers': ['errorFile'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'sync_log': {
            'handlers': ['syncFile'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(BASE_DIR, "static/"))


MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, "media/"))
MEDIA_URL = '/media/'

# 跨域允许的请求方式，可以使用默认值，默认的请求方式为:
# from corsheaders.defaults import default_methods
CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
)

# 允许跨域的请求头，可以使用默认值，默认的请求头为:
# from corsheaders.defaults import default_headers
# CORS_ALLOW_HEADERS = default_headers

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

# 跨域请求时，是否运行携带cookie，默认为False
CORS_ALLOW_CREDENTIALS = True
# 允许所有主机执行跨站点请求，默认为False
# 如果没设置该参数，则必须设置白名单，运行部分白名单的主机才能执行跨站点请求
CORS_ORIGIN_ALLOW_ALL = True

AUTH_USER_MODEL = 'user.User'

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=365),
    'JWT_ALLOW_REFRESH': True,
}

if DEBUG:
    try:
        from .local_settings import *
    except ImportError:
        pass

COMMON_READ_ONLY_FIELDS = ('created_time', 'last_updated_time', 'delete_time',
                           'delete_flag', 'created_user', 'last_updated_user',
                           'delete_user')