from django.core.mail import send_mail

from django_jwt_2fa.settings import JWT_2FA_SETTINGS


class EmailOTPBackend:
    @staticmethod
    def send(email, code):
        send_mail(
            JWT_2FA_SETTINGS["EMAIL_SUBJECT"],
            f"Your verification code is {code}",
            JWT_2FA_SETTINGS["EMAIL_FROM"],
            [email],
            fail_silently=False,
        )
