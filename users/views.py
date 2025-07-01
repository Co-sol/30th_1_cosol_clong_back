from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSignupSerializer, UserLoginSerializer, EmailCheckSerializer
from rest_framework.permissions import IsAuthenticated

class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'message': '회원가입이 완료되었습니다.',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'name': user.name,
                'clean_sense': user.clean_sense,
                'profile': user.profile,
                'evaluation_status': user.evaluation_status,
            },
        }, status=status.HTTP_201_CREATED)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': '로그인 성공',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response({
                'message': '로그아웃 성공',
            }, status=status.HTTP_200_OK)

            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')

            return response

        except TokenError:
            return Response({
                'message': '로그아웃 성공',
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': '로그아웃 처리 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class EmailCheckView(generics.GenericAPIView):
    """이메일 중복 확인 API"""
    serializer_class = EmailCheckSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'message': '사용 가능한 이메일입니다.',
                'available': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': '이미 사용 중인 이메일입니다.',
                'available': False,
            }, status=status.HTTP_400_BAD_REQUEST)