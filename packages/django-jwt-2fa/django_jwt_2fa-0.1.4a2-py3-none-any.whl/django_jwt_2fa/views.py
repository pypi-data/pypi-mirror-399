# django_jwt_2fa/views.py

import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django_jwt_2fa.authentication import EmailOTPBackend


class Verify2FAView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        temp_token = request.data.get("temp_token")
        otp = request.data.get("otp")

        if not temp_token or not otp:
            return Response({"message": "OTP and token required"}, status=400)

        try:
            payload = jwt.decode(
                temp_token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return Response({"message": "Token expired"}, status=401)

        if not payload.get("2fa_pending"):
            return Response({"message": "Invalid token"}, status=400)

        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = User.objects.get(id=payload["user_id"])

        EmailOTPBackend().verify(user, otp)

        if not settings.JWT_2FA_FINAL_TOKEN_ISSUER:
            return Response(
                {"message": "Final token issuer not configured"},
                status=500,
            )

        # Call consumer-provided token generator
        token = settings.JWT_2FA_FINAL_TOKEN_ISSUER(user)

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return Response(
            {
                "message": "2FA verification successful",
                "data": token,
            }
        )
