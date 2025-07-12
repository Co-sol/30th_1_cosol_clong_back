# chatbot/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .openai_utils import get_chat_response
from .models import ChatMessage

class ChatbotAskView(APIView):
    def post(self, request):
        try:
            user_message = request.data.get("message")
            if not user_message:
                return Response({
                    'success': False,
                    "message": "메시지를 입력해주세요."
                }, status=status.HTTP_400_BAD_REQUEST)

            last = ChatMessage.objects.filter(user=request.user).order_by("-order_number").first()
            order_number = last.order_number + 1 if last else 1

            ChatMessage.objects.create(
                user=request.user,
                role='user',
                message=user_message,
                order_number=order_number
            )

            history = ChatMessage.objects.filter(user=request.user).order_by("order_number")
            chat_history = [{"role": msg.role, "content": msg.message} for msg in history]

            bot_response = get_chat_response(chat_history)

            if bot_response.startswith("Error:"):
                return Response({
                    'success': False,
                    'message': '챗봇 서비스에 일시적인 오류가 발생했습니다.',
                    'data': bot_response
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 응답 저장
            ChatMessage.objects.create(
                user=request.user,
                role="assistant",
                message=bot_response,
                order_number=order_number + 1
            )

            return Response({
                'success': True,
                'message': "챗봇 응답 생성을 완료하였습니다",
                "data": bot_response
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'message': '챗봇 서비스에 일시적인 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatbotHistoryView(APIView):
    def get(self, request):
        try:
            messages = ChatMessage.objects.filter(user=request.user).order_by("order_number")
            data = [
                {
                    "order_number": msg.order_number,
                    "role": msg.role,
                    "message": msg.message,
                    "timestamp": msg.created_at,
                }
                for msg in messages
            ]
            return Response({
                "success": True,
                "message": "대화 목록 조회에 성공하였습니다.",
                "data": data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "이력 조회 중 오류가 발생했습니다."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
