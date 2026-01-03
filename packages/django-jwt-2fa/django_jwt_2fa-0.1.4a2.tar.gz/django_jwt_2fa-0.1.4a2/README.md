# django-jwt-2fa

Role-aware JWT-based 2FA for Django REST Framework.

## Features

- **Role-based 2FA**: Require 2FA only for specific user roles.
- **JWT Integration**: Seamlessly integrates with `djangorestframework-simplejwt`.
- **Email OTP**: Sends One-Time Passwords via email.
- **Secure**: Basic security features like OTP expiry and hash verification.

## Requirements

- Python >= 3.12
- Django >= 6.0
- Django REST Framework
- djangorestframework-simplejwt

## Installation

Install via pip:

```bash
pip install django-jwt-2fa
```

## Configuration

1. **Add to Installed Apps**

   Add `django_jwt_2fa` to your `INSTALLED_APPS` in `settings.py`:

   ```python
   INSTALLED_APPS = [
       ...
       "rest_framework",
       "rest_framework_simplejwt",
       "django_jwt_2fa",
       ...
   ]
   ```

2. **Run Migrations**

   Create the necessary tables for OTP storage:

   ```bash
   python manage.py migrate
   ```

3. **Configure Settings**

   Add the `JWT_2FA` configuration to your `settings.py`. You can customize the behavior as needed:

   ```python
   JWT_2FA = {
       "ROLE_FIELD": "role",  # Field on User model to check role
       "REQUIRE_2FA_FOR_ROLES": ["employee", "admin"],  # Roles that require 2FA
       "OTP_EXPIRY_SECONDS": 300,  # OTP validity duration (5 minutes)
       "EMAIL_SUBJECT": "Your verification code",
       "EMAIL_FROM": "noreply@example.com",  # Sender email address
       "MAX_2FA_AGE_SECONDS": 43200,  # Time before 2FA re-verification is needed (12 hours)
   }
   ```

   **Defaults:**

   - `ROLE_FIELD`: "role"
   - `REQUIRE_2FA_FOR_ROLES`: ["employee"]
   - `OTP_EXPIRY_SECONDS`: 300
   - `MAX_2FA_AGE_SECONDS`: 12 hours

## Usage

### 1. URL Configuration

Add the verification endpoint to your `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... your other urls
    path("api/auth/2fa/", include("django_jwt_2fa.urls")),
]
```

This exposes `POST /api/auth/2fa/verify/`.

### 2. Protecting Views

Use the `Require2FAIfConfigured` permission class to protect your views. This permission checks if:

1. The user is authenticated.
2. The user's role requires 2FA (based on your settings).
3. If 2FA is required, it checks if the 2FA verification is complete and valid.

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_jwt_2fa.permissions import Require2FAIfConfigured

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated, Require2FAIfConfigured]

    def get(self, request):
        return Response({"message": "You have passed 2FA!"})
```

### 3. Verification Flow

1. **Initial Login**: User logs in normally via your existing JWT login endpoint to get an initial access token.
2. **2FA Trigger**: If the user tries to access a protected view and hasn't verified 2FA, they will receive a `403 Forbidden`.
   *Note: Your application logic should handle the flow to request OTP sending (not covered by this package purely, usually part of your login or a specific 'send-otp' endpoint you might implement using `OTPService` if exposed, or the system sends it automatically upon login triggers - *check specific implementation details*).*
   *Wait, looking at the code, this package currently provides the *verification* view and permission. You might need to implement the mechanism to *send* the OTP or ensure it's generated.*

3. **Verify OTP**:
   Send a POST request to the verification endpoint:

   **POST** `/api/auth/2fa/verify/`

   **Headers:**
   `Authorization: Bearer <your_access_token>`

   **Body:**

   ```json
   {
   	"code": "123456"
   }
   ```

   **Response:**
   Returns a _new_ pair of Access and Refresh tokens. These tokens contain the `is_2fa_verified: true` claim.

   ```json
   {
   	"access": "eyJhbG...",
   	"refresh": "eyJhbG..."
   }
   ```

4. **Access Protected Resources**: use the _new_ access token to access views protected by `Require2FAIfConfigured`.
