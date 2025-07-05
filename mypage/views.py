from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserInfoSerializer
from rest_framework.permissions import AllowAny

# Create your views here.
class UserInfoView(generics.GenericAPIView):
    serializer_class = UserInfoSerializer

    def get(self, request):
        user = request.user
        serializer = self.get_serializer(user)

        return Response({
            'success': True,
            'message': '사용자 정보 조회에 성공하였습니다.',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': '사용자 정보 수정에 성공하였습니다.',
                'data': serializer.data,
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                'success': False,
                'errors': serializer.errors,
                'message': '입력한 데이터를 확인해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)