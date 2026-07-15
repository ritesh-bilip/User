from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
# import uuid
# Create your models here.
class UserManager(BaseUserManager):
  def create_user(self,email,name,phone_number,password=None):
    if not email:
      raise ValueError("Must enter Email")
    user=self.model(
      email=self.normalize_email(email),
      name=name,
      phone_number=phone_number
    )
    user.set_password(password)
    user.save(using=self._db)
    return user
  def create_superuser(self,email,name,phone_number,password):
    user=self.create_user(email,name,phone_number,password)
    user.is_admin=True
    user.save(using=self._db)
    return user
class User(AbstractBaseUser):
  name=models.CharField(max_length=100)
  email=models.EmailField(unique=True)
  phone_number=models.CharField(max_length=10,blank=True,null=True)
  is_active=models.BooleanField(default=True)
  is_admin=models.BooleanField(default=False)
  objects=UserManager()
  USERNAME_FIELD='email'
  REQUIRED_FIELDS=['name','phone_number']
  def __str__(self):
    return self.email
  def has_perm(self,perm,obj=None):
    return True
  def has_module_perms(self,app_label):
    return True
  @property
  def is_staff(self):
    return self.is_admin




class Profile(models.Model):
  user = models.OneToOneField(User,on_delete=models.CASCADE)
  avatar=models.ImageField(upload_to="avatars",blank=True,null=True)
  bio=models.TextField(blank=True)
  created_at=models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.user.email

# class OTP(models.Model):
#   user=models.ForeignKey(User,on_delete=models.CASCADE)
#   code=models.CharField(max_length=6)
#   created_at=models.DateTimeField(auto_now_add=True)
#   is_verified=models.BooleanField(default=False)

#   def __str__(self):
#     return f"{self.user.username} - {self.code}"