from django.urls import path
from .views import (
    UserInfoView,
    UserWithdrawView,
)

app_name = 'mypage'

urlpatterns = [
    path('info/', UserInfoView.as_view(), name='user_info'),
    path('withdraw/', UserWithdrawView.as_view(), name='user_withdraw'),
]