from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.extensions import OpenApiAuthenticationExtension

class LightweightJWTUser:

    def __init__(self, payload):
        self.id = payload.get('user_id')
        self.role = payload.get('role')
        self.is_staff = payload.get('is_staff')
        self.is_superuser = payload.get('is_superuser')
        self.email = payload.get('email')
        self.name = payload.get('name')  # <-- Add this line
        self.is_authenticated = True

class LightweightJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        # Use only JWT claims, do NOT hit the database
        return LightweightJWTUser(validated_token)

class LightweightJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = 'users.auth.LightweightJWTAuthentication'
    name = 'Bearer'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
