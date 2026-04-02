import os
import random
import threading
import logging
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP, Profile
from .serializer import UserSerializer, ProfileSerializer
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)

def send_otp_email_async(subject, message, recipient):
    """Non-blocking email with error logging"""
    try:
        from django.conf import settings
        from_email = settings.DEFAULT_FROM_EMAIL  # explicitly use verified sender
        msg = EmailMessage(subject, message, from_email, [recipient])
        msg.send(fail_silently=False)  # ← CHANGED: don't silence errors
        logger.info(f"OTP email sent successfully to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {recipient}: {str(e)}")


class SignupView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        code = str(random.randint(100000, 999999))
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)
        OTP.objects.create(user=user, code=code)

        threading.Thread(
            target=send_otp_email_async,
            args=('Your OTP', f'Your OTP is {code}', user.email)
        ).start()

        return Response({"message": "Signup successful. OTP sent to email."}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            code = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, code=code)

            threading.Thread(
                target=send_otp_email_async,
                args=('Your Login OTP', f'Your OTP is {code}', user.email)
            ).start()

            return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class VerifyOTPView(APIView):
    def post(self, request):
        username = request.data.get("username")
        code = request.data.get("otp")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        otp = OTP.objects.filter(user=user, code=code, is_verified=False).last()
        if otp:
            otp.is_verified = True
            otp.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def landing_page(request): return render(request, 'landing.html')
def auth_page(request): return render(request, 'auth.html')
def dashboard_page(request): return render(request, 'dashboard.html')
class DebugEmailView(APIView):
    def get(self, request):
        from django.conf import settings
        import threading
        
        # Test send synchronously (not async) to see the real error
        try:
            from django.core.mail import EmailMessage
            msg = EmailMessage(
                'Test OTP',
                'This is a test OTP: 123456',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL]  # send to yourself
            )
            msg.send(fail_silently=False)
            return Response({
                "status": "Email sent!",
                "from": settings.DEFAULT_FROM_EMAIL,
                "host": settings.EMAIL_HOST,
                "user": settings.EMAIL_HOST_USER,
                "api_key_set": bool(settings.EMAIL_HOST_PASSWORD),
                "api_key_prefix": settings.EMAIL_HOST_PASSWORD[:10] if settings.EMAIL_HOST_PASSWORD else None
            })
        except Exception as e:
            return Response({
                "error": str(e),
                "from": settings.DEFAULT_FROM_EMAIL,
                "host": settings.EMAIL_HOST,
                "user": settings.EMAIL_HOST_USER,
                "api_key_set": bool(settings.EMAIL_HOST_PASSWORD),
                "api_key_prefix": settings.EMAIL_HOST_PASSWORD[:10] if settings.EMAIL_HOST_PASSWORD else None
            }, status=400)
        
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "username": request.user.username,
            "email": request.user.email,
        })

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({"message": "If that email exists, a reset code was sent."})
        
        code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, code=code)
        threading.Thread(
            target=send_otp_email_async,
            args=('Password Reset OTP', f'Your password reset OTP is {code}. It expires in 10 minutes.', user.email)
        ).start()
        return Response({"message": "If that email exists, a reset code was sent."})

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("otp")
        new_password = request.data.get("new_password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = OTP.objects.filter(user=user, code=code, is_verified=False).last()
        if not otp:
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        otp.is_verified = True
        otp.save()
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful!"})