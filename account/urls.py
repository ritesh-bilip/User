from django.urls import path
from .views import *

urlpatterns = [
    # Api routes
    # path('', landing_page, name='landing'),
    path('auth-page-register/', UserRegistrationView.as_view(), name='auth_page_register'),
    path('auth-page-login/',UserLoginView.as_view(),name="auth_page_login"),
    path('profile/',UserProfileView.as_view(),name='profile'),

    # template
    path('', landing_page, name='landing'),
    path('auth-page/', auth_page, name='signup'),
    path('dashboard/',dashboard_page,name='dashboard')
]