
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import smart_text
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings


class DisableCSRF(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        setattr(request, '_dont_enforce_csrf_checks', True)
