from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSignupSerializer, UserLoginSerializer, EmailCheckSerializer
from rest_framework.permissions import AllowAny


class UserSignupView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    serializer_class = UserSignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            return Response({
                'success': True,
                'message': '회원가입이 완료되었습니다.',
                'data': {
                    'id': str(user.id),
                    'email': user.email,
                    'name': user.name,
                    'clean_sense': user.clean_sense,
                    'profile': user.profile,
                    'evaluation_status': user.evaluation_status,
                },
            }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            if isinstance(e.detail, dict):
                if 'name' in e.detail or 'email' in e.detail or 'password' in e.detail or 'clean_sense' in e.detail:
                    return Response({
                        'success': False,
                        'message': "필드를 모두 입력해주세요."
                    }, status=status.HTTP_400_BAD_REQUEST)
                elif 'message' in e.detail:
                    return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'success': False,
                "message": "입력 정보를 확인해주세요."}
            , status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)
            return Response({
                'success': True,
                'message': '로그인이 완료되었습니다.',
                'data': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })

        except serializers.ValidationError as e:
            if isinstance(e.detail, dict):
                if 'email' in e.detail or 'password' in e.detail:
                    return Response({
                        'success': False,
                        "message": "필드를 모두 입력해주세요."
                    }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'success': False,
                "message": "로그인 정보를 확인해주세요."
            }, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response({
                'success': True,
                'message': '로그아웃 성공',
            }, status=status.HTTP_200_OK)

            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')

            return response

        except TokenError:
            return Response({
                'success': True,
                'message': '로그아웃 성공',
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': '로그아웃 처리 중 오류가 발생했습니다.',
            }, status=status.HTTP_400_BAD_REQUEST)

class EmailCheckView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    serializer_class = EmailCheckSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            return Response({
                'success': True,
                'message': '사용 가능한 이메일입니다.',
                'available': True
            }, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            error_detail = e.detail

            if isinstance(e.detail, dict):
                message = error_detail['email'][0]

                if message == "이미 사용 중인 이메일입니다.":
                    return Response({
                        'success': True,
                        'message': message,
                        'available': False,
                    }, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({
                        'success': False,
                        'message': message,
                        'available': False,
                    }, status=status.HTTP_400_BAD_REQUEST)