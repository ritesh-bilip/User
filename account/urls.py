from django.urls import path
from .views import SignupView, LoginView, VerifyOTPView, ProfileView, landing_page, auth_page, dashboard_page

urlpatterns = [
    # Template routes
    path('', landing_page, name='landing'),
    path('auth-page/', auth_page, name='auth_page'),
    path('dashboard/', dashboard_page, name='dashboard'),

    # API routes
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('profile/', ProfileView.as_view(), name='profile'),
]