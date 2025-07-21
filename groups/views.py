from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import GenericAPIView, UpdateAPIView
from .serializers import (
    CheckUserSerializer,
    GroupCreateSerializer,
    GroupInfoSeriazlier,
    GroupMemberSerializer,
    GroupUpdateSerializer,
)
from .models import Group
from users.models import User


# 유저 조회 API
class CheckUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckUserSerializer

    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "errorCode": "USER_NOT_FOUND",
                    "message": "존재하지 않는 사용자입니다: " + email,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.group_id:  # 이미 다른 그룹에 속해 있는 경우
            return Response(
                {
                    "success": False,
                    "errorCode": "USER_ALREADY_IN_GROUP",
                    "message": "이미 다른 그룹에 속한 사용자입니다: " + email,
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.get_serializer(user)
        return Response(
            {
                "success": True,
                "message": "다른 유저 조회 완료",
                "data": {
                    "userExists": True,
                    "userInfo": serializer.data,
                    "canInvite": True,
                    "invitestatus": "AVAILABLE",
                },
            },
            status=status.HTTP_200_OK,
        )


# 그룹 새성 API
class GroupCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            group = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "그룹 생성이 완료되었습니다.",
                    "data": {"groupId": group.group_id},
                },
                status=status.HTTP_201_CREATED,
            )

        except serializers.ValidationError as e:
            return Response(
                {
                    "success": False,
                    "errorCode": "MISSING_REQUIRED_FIELDS",
                    "message": "그룹명을 입력해주세요.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class GroupInfoView(GenericAPIView):
    serializer_class = GroupInfoSeriazlier
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "errorCode": "GROUP_NOT_FOUND",
                    "message": f"해당 ID에 해당하는 그룹이 존재하지 않습니다. {group_id}",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = self.get_serializer(group).data
        return Response(
            {
                "success": True,
                "message": "그룹 정보 조회에 성공했습니다.",
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class GroupUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupUpdateSerializer
    lookup_url_kwarg = "group_id"

    def get_queryset(self):
        return Group.objects.all()

    def patch(self, request, *args, **kwargs):
        group_id = self.kwargs.get("group_id")
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "errorCode": "GROUP_NOT_FOUND",
                    "message": f"해당 ID에 해당하는 그룹이 존재하지 않습니다. {group_id}",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(group, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "success": True,
                "message": "그룹 정보 수정에 성공하였습니다.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GroupMemberInfoView(GenericAPIView):
    def get(self, request, group_id):
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "errorCode": "GROUP_NOT_FOUND",
                    "message": f"해당 ID에 해당하는 그룹이 존재하지 않습니다. {group_id}",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        users = User.objects.filter(group=group)
        serializer = GroupMemberSerializer(users, many=True)

        return Response(
            {
                "success": True,
                "message": "그룹원 정보 조회에 성공하였습니다.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
