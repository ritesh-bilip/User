from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.
class Profile(models.Model):
  user = models.OneToOneField(User,on_delete=models.CASCADE)
  avatar=models.ImageField(upload_to="avatars",blank=True,null=True)
  bio=models.TextField(blank=True)
  created_at=models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.user.username

class OTP(models.Model):
  user=models.ForeignKey(User,on_delete=models.CASCADE)
  code=models.CharField(max_length=6)
  created_at=models.DateTimeField(auto_now_add=True)
  is_verified=models.BooleanField(default=False)

  def __str__(self):
    return f"{self.user.username} - {self.code}"