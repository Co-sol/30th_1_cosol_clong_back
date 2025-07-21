from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt import serializers
from .serializers import UserInfoSerializer
from users.models import User
from checklists.models import Checklistitem
from django.contrib.auth import get_user_model


# Create your views here.
class UserInfoView(generics.GenericAPIView):
    serializer_class = UserInfoSerializer

    def get(self, request):
        try:
            user = request.user
            serializer = self.get_serializer(user)

            return Response(
                {
                    "success": True,
                    "message": "사용자 정보 조회에 성공하였습니다.",
                    "data": {
                        **serializer.data,
                        "IsInGroup": bool(user.group_id),
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "사용자 정보 조회 중 오류가 발생했습니다.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request):
        try:
            user = request.user
            serializer = self.get_serializer(user, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "사용자 정보 수정에 성공하였습니다.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")

                return Response(
                    {
                        "success": False,
                        "message": (
                            ", ".join(error_messages)
                            if error_messages
                            else "입력한 데이터를 확인해주세요."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "사용자 정보 수정 중 오류가 발생했습니다.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserWithdrawView(generics.GenericAPIView):
    User = get_user_model

    def post(self, request):
        try:
            user = request.user

            if not user or not user.is_active:
                return Response(
                    {"success": False, "message": "유효하지 않은 사용자입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.delete()

            return Response(
                {"success": True, "message": "회원 탈퇴가 완료되었습니다."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"success": False, "message": "회원 탈퇴 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LeaveGroupView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user: User = request.user

        if not user.group:
            return Response(
                {
                    "success": False,
                    "errorCode": "NO_GROUP_TO_LEAVE",
                    "message": "현재 소속된 그룹이 없습니다.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            Checklistitem.objects.filter(user=user).delete()
            user.group = None
            user.save()

        return Response(
            {"success": True, "message": "그룹 탈퇴가 완료되었습니다."},
            status=status.HTTP_200_OK,
        )
