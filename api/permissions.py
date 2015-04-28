from rest_framework import permissions
from django.conf import settings

class WhiteListPermission(permissions.BasePermission):
    """
        Global permission check for api.data.gov IPs
    """
    def has_permission(self, request, view):
        ip_addr = None
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            try:
                ip_addr = forwarded.split(',')[-2].strip()
            except:
                ip_addr = forwarded
        else:
            ip_addr = request.META['REMOTE_ADDR']

        if settings.REST_FRAMEWORK['WHITELIST']:
            if ip_addr in settings.REST_FRAMEWORK['WHITELIST']:
                return True
            else:
                return False
        else:
            return True
