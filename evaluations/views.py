from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import GroupEvalCreateSerializer, GroupEvalResponseSerializer
from rest_framework.permissions import IsAuthenticated

class GroupEvalCreateView(APIView):  # 평가 진행
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = GroupEvalCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            evals = serializer.save()
            response_serializer = GroupEvalResponseSerializer(evals, many=True)
            return Response({
                "status": 201,
                "success": True,
                "message": "그룹 평가가 성공적으로 등록되었습니다.",
                "data": response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": 400,
            "success": False,
            "message": f"유효성 검사를 실패했습니다."
        }, status=status.HTTP_400_BAD_REQUEST)


