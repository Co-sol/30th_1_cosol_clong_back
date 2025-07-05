from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt import serializers
from .serializers import UserInfoSerializer

# Create your views here.
class UserInfoView(generics.GenericAPIView):
    serializer_class = UserInfoSerializer

    def get(self, request):
        try:
            user = request.user
            serializer = self.get_serializer(user)

            return Response({
                'success': True,
                'message': '사용자 정보 조회에 성공하였습니다.',
                'data': serializer.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'message': '사용자 정보 조회 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
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
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")

                return Response({
                    'success': False,
                    'message': ', '.join(error_messages) if error_messages else '입력한 데이터를 확인해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'message': '사용자 정보 수정 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


