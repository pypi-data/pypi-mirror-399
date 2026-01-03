import time

from rest_framework.permissions import BasePermission

from django_jwt_2fa.settings import JWT_2FA_SETTINGS


class Require2FAIfConfigured(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = getattr(user, JWT_2FA_SETTINGS["ROLE_FIELD"], None)
        if role not in JWT_2FA_SETTINGS["REQUIRE_2FA_FOR_ROLES"]:
            return True

        auth = request.auth or {}
        if not auth.get("is_2fa_verified"):
            return False

        issued_at = auth.get("2fa_at")
        if not issued_at:
            return False

        if issued_at > time.time():
            return False

        max_age = JWT_2FA_SETTINGS.get("MAX_2FA_AGE_SECONDS")
        return (time.time() - issued_at) <= max_age
