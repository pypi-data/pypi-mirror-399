class TwoFATokenMixin:
    @classmethod
    def add_2fa_claims(cls, token, user):
        token["is_2fa_verified"] = False
        return token
