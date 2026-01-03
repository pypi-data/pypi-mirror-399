import secrets

from django.utils.crypto import salted_hmac


class OTPService:
    @staticmethod
    def generate_code():
        return f"{secrets.randbelow(1_000_000):06}"

    @staticmethod
    def hash_code(code):
        return salted_hmac("jwt-2fa", code).hexdigest()

    @staticmethod
    def verify(code, hashed):
        return salted_hmac("jwt-2fa", code).hexdigest() == hashed
