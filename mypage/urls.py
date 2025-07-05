from django.urls import path
from .views import (
    UserInfoView,
)

app_name = 'mypage'

urlpatterns = [
    path('info/', UserInfoView.as_view(), name='get_user_info'),
]