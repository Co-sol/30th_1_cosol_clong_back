from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from .serializers import CheckUserSerializer, GroupCreateSerializer
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


            )
