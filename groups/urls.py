from django.urls import path
from .views import CheckUserView, GroupCreateView

urlpatterns = [
    path("check-user/<str:email>/", CheckUserView.as_view(), name="check_user"),
    path("create/", GroupCreateView.as_view(), name="create_group"),
]
