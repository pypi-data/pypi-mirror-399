from django.conf import settings
from django.core.mail import send_mail

from django_jwt_2fa.utils.otp import generate_email_otp


def send_otp_email(user):
    otp = generate_email_otp(user)

    send_mail(
        subject="Your login verification code",
        message=f"Your verification code is {otp}. It expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
