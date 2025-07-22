from django.urls import path
from .views import (
    CheckUserView,
    GroupCreateView,
    GroupInfoView,
    GroupMemberInfoView,
    GroupUpdateView,
)

urlpatterns = [
    path("check-user/", CheckUserView.as_view(), name="check_user"),
    path("create/", GroupCreateView.as_view(), name="create_group"),
    path("group-info/", GroupInfoView.as_view(), name="group_info"),
    path("modify/", GroupUpdateView.as_view(), name="modify_group"),
    path("member-info/", GroupMemberInfoView.as_view(), name="member-info"),
]
