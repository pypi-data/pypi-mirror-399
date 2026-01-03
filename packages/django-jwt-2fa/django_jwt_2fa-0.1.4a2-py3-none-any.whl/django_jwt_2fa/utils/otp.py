import random
from datetime import timedelta

from django.utils import timezone

from django_jwt_2fa.models import EmailOTP


def generate_email_otp(user):
    otp = str(random.randint(100000, 999999))
    print(f"Generated OTP for {user.email}: {otp}")  # For debugging purposes
    EmailOTP.objects.create(
        user=user,
        otp=otp,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    return otp
