import time
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailOTP
from .serializers import VerifyOTPSerializer
from .services.otp import OTPService
from .settings import JWT_2FA_SETTINGS

User = get_user_model()


class Verify2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = (
            EmailOTP.objects.filter(user_id=request.user.id, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return Response({"detail": "OTP not found"}, status=400)

        if otp.is_expired(timedelta(seconds=JWT_2FA_SETTINGS["OTP_EXPIRY_SECONDS"])):
            return Response({"detail": "OTP expired"}, status=400)

        if not OTPService.verify(serializer.validated_data["code"], otp.code_hash):
            return Response({"detail": "Invalid code"}, status=400)

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        refresh = RefreshToken.for_user(request.user)
        refresh["is_2fa_verified"] = True
        refresh["2fa_at"] = int(time.time())

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )
