from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed

from django_jwt_2fa.models import EmailOTP


class EmailOTPBackend:
    def verify(self, user, otp):
        try:
            record = EmailOTP.objects.filter(
                user=user,
                otp=otp,
                is_used=False,
                expires_at__gte=timezone.now(),
            ).latest("created_at")
        except EmailOTP.DoesNotExist:
            raise AuthenticationFailed("Invalid or expired OTP")

        record.is_used = True
        record.save()
        return True
