import os
import random
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP, Profile
from .serializer import UserSerializer, ProfileSerializer




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
        try:
            send_mail(
                'Your OTP',
                f'Your OTP is {code}',
                None,  # Uses your verified Gmail from settings
                [user.email],
                fail_silently=False,
           )
        except Exception as e:
            return Response({"error": f"Email failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)                    
        return Response({"message": "Signup successful. OTP sent to email."}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            code = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, code=code)
            try:
                send_mail(
                    'Your OTP',
                    f'Your OTP is {code}',
                    None,  # Uses your verified Gmail from settings
                    [user.email],
                    fail_silently=False,
              )
            except Exception as e:
                return Response({"error": f"Email failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
            
            return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class VerifyOTPView(APIView):
    def post(self, request):
        username = request.data.get("username")
        code = request.data.get("otp")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:   # ✅ fixed typo
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
        serializer = ProfileSerializer(profile)   # ✅ fixed
        return Response(serializer.data)

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Template Views
def landing_page(request):
    return render(request, 'landing.html')

def auth_page(request):
    return render(request, 'auth.html')

def dashboard_page(request):
    return render(request, 'dashboard.html')