from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import *
from .serializer import *

# ✅ Import CustomRefreshToken (defined in serializer.py)
# so registration and login both produce tokens with name baked in.
from .serializer import CustomRefreshToken


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # ✅ FIX: was RefreshToken.for_user(user)
            # CustomRefreshToken adds name + email to the payload
            refresh = CustomRefreshToken.for_user(user)

            return Response({
                "email": user.email,
                "name": user.name,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserprofileSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data)

    def get_object(self):
        return self.request.user


def landing_page(request): return render(request, 'landing.html')
def auth_page(request): return render(request, 'auth.html')
def dashboard_page(request): return render(request, 'dashboard.html')
#! for onlie Otp loging in system 



# def send_otp_email_async(subject, message, recipient):
#     def _send():
#         try:
#             mail = Mail(
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 to_emails=recipient,
#                 subject=subject,
#                 plain_text_content=message
#             )
#             sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
#             response = sg.send(mail)
#             logger.info(f"OTP email sent to {recipient} — status {response.status_code}")
#         except Exception as e:
#             logger.error(f"Failed to send OTP email to {recipient}: {str(e)}")
#     threading.Thread(target=_send).start()


# class SignupView(APIView):
#     def post(self, request):
#         username = request.data.get("username")
#         email = request.data.get("email")
#         password = request.data.get("password")

#         if User.objects.filter(username=username).exists():
#             return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
#         if User.objects.filter(email=email).exists():
#             return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

#         code = str(random.randint(100000, 999999))
#         user = User.objects.create_user(username=username, email=email, password=password)
#         Profile.objects.create(user=user)
#         OTP.objects.create(user=user, code=code)

#         threading.Thread(
#             target=send_otp_email_async,
#             args=('Your OTP', f'Your OTP is {code}', user.email)
#         ).start()

#         return Response({"message": "Signup successful. OTP sent to email."}, status=status.HTTP_201_CREATED)


# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")
#         user = authenticate(username=username, password=password)

#         if user is not None:
#             code = str(random.randint(100000, 999999))
#             OTP.objects.create(user=user, code=code)

#             threading.Thread(
#                 target=send_otp_email_async,
#                 args=('Your Login OTP', f'Your OTP is {code}', user.email)
#             ).start()

#             return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

#         return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# class VerifyOTPView(APIView):
#     def post(self, request):
#         username = request.data.get("username")
#         code = request.data.get("otp")
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#         otp = OTP.objects.filter(user=user, code=code, is_verified=False).last()
#         if otp:
#             otp.is_verified = True
#             otp.save()
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }, status=status.HTTP_200_OK)

#         return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


# class ProfileView(APIView):
#     def get(self, request):
#         profile = Profile.objects.get(user=request.user)
#         serializer = ProfileSerializer(profile)
#         return Response(serializer.data)

#     def put(self, request):
#         profile = Profile.objects.get(user=request.user)
#         serializer = ProfileSerializer(profile, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# class DebugEmailView(APIView):
#     def get(self, request):
#         from django.conf import settings
#         import threading
        
#         # Test send synchronously (not async) to see the real error
#         try:
#             from django.core.mail import EmailMessage
#             msg = EmailMessage(
#                 'Test OTP',
#                 'This is a test OTP: 123456',
#                 settings.DEFAULT_FROM_EMAIL,
#                 [settings.DEFAULT_FROM_EMAIL]  # send to yourself
#             )
#             msg.send(fail_silently=False)
#             return Response({
#                 "status": "Email sent!",
#                 "from": settings.DEFAULT_FROM_EMAIL,
#                 "host": settings.EMAIL_HOST,
#                 "user": settings.EMAIL_HOST_USER,
#                 "api_key_set": bool(settings.EMAIL_HOST_PASSWORD),
#                 "api_key_prefix": settings.EMAIL_HOST_PASSWORD[:10] if settings.EMAIL_HOST_PASSWORD else None
#             })
#         except Exception as e:
#             return Response({
#                 "error": str(e),
#                 "from": settings.DEFAULT_FROM_EMAIL,
#                 "host": settings.EMAIL_HOST,
#                 "user": settings.EMAIL_HOST_USER,
#                 "api_key_set": bool(settings.EMAIL_HOST_PASSWORD),
#                 "api_key_prefix": settings.EMAIL_HOST_PASSWORD[:10] if settings.EMAIL_HOST_PASSWORD else None
#             }, status=400)
        
# class UserDetailView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         return Response({
#             "username": request.user.username,
#             "email": request.user.email,
#         })

# class ForgotPasswordView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             # Don't reveal if email exists
#             return Response({"message": "If that email exists, a reset code was sent."})
        
#         code = str(random.randint(100000, 999999))
#         OTP.objects.create(user=user, code=code)
#         threading.Thread(
#             target=send_otp_email_async,
#             args=('Password Reset OTP', f'Your password reset OTP is {code}. It expires in 10 minutes.', user.email)
#         ).start()
#         return Response({"message": "If that email exists, a reset code was sent."})

# class ResetPasswordView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         code = request.data.get("otp")
#         new_password = request.data.get("new_password")
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        
#         otp = OTP.objects.filter(user=user, code=code, is_verified=False).last()
#         if not otp:
#             return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
#         otp.is_verified = True
#         otp.save()
#         user.set_password(new_password)
#         user.save()
#         return Response({"message": "Password reset successful!"})