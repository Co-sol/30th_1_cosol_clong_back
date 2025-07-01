from django.urls import path
from .views import (
    UserSignupView,
    UserLoginView,
    UserLogoutView,
    EmailCheckView,
)
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'users'

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='user_signup'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('email-check/', EmailCheckView.as_view(), name='email_check'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]