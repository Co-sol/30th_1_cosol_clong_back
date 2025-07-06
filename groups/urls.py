from django.urls import path
from .views import CheckUserView, GroupCreateView

urlpatterns = [
    path("check-user/<str:email>/", CheckUserView.as_view(), name="check_user"),
]
