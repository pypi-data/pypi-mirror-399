from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken


def get_temp_token(user):
    token = AccessToken.for_user(user)

    token["2fa_pending"] = True
    token["user_id"] = user.id

    # VERY short expiry
    token.set_exp(lifetime=timedelta(minutes=5))

    return str(token)
