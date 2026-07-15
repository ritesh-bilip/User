from rest_framework.serializers import ModelSerializer
# from django.contrib.auth.models import User
from .models import Profile,User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


# ✅ FIX: Bake the user's real name into the JWT payload.
# SimpleJWT by default only stores user_id, exp, jti etc.
# The chat service reads payload.name to identify the user,
# so without this, it always falls back to "User_<id>".
class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token['name'] = user.name    # → now payload.name = "Ritesh"
        token['email'] = user.email  # bonus: available as fallback
        return token

class UserRegistationSerializer(serializers.ModelSerializer):
  password=serializers.CharField(write_only=True)
  class Meta:
    model=User
    fields=['name','email','phone_number','password']
  def create(self,validated_data):
    user=User.objects.create_user(
      name=validated_data['name'],
      email=validated_data['email'],
      phone_number=validated_data['phone_number'],
      password=validated_data['password']
    )
    return user
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        # 💡 Pass 'email' into the 'username' keyword argument
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        
        refresh = CustomRefreshToken.for_user(user)  # ← was RefreshToken
        return {
            "email": user.email,
            "name": user.name,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
class UserprofileSerializer(ModelSerializer):
  class Meta:
    model=Profile
    fields=['id','avatar','bio','created_at']