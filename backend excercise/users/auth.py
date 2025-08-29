from rest_framework_simplejwt.authentication import JWTAuthentication

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
