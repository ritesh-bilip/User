from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import Profile

class UserSerializer(ModelSerializer):
  class Meta:
    model=User
    fields=['id','username','email']

class ProfileSerializer(ModelSerializer):
  class Meta:
    model=Profile
    fields=['id','avatar','bio','created_at']