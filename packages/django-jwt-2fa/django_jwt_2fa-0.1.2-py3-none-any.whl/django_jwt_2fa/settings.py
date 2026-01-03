from django.conf import settings

DEFAULTS = {
    "ROLE_FIELD": "role",
    "REQUIRE_2FA_FOR_ROLES": ["employee"],
    "OTP_EXPIRY_SECONDS": 300,
    "EMAIL_SUBJECT": "Your verification code",
    "EMAIL_FROM": None,
    "MAX_2FA_AGE_SECONDS": 12 * 60 * 60,
}

JWT_2FA_SETTINGS = {**DEFAULTS, **getattr(settings, "JWT_2FA", {})}
