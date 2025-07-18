from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
from .models import GroupEval
from datetime import datetime, timedelta
from .serializers import (
    GroupEvalCreateSerializer, 
    GroupEvalResponseSerializer,
    GroupEvalAverageSerializer,
)
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

class GroupEvalAverageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.today()
        last_sunday = today - timedelta(days=today.weekday() + 1)
        prev_week_start = last_sunday - timedelta(days=7)
        prev_week_start_date = prev_week_start.date()

        user = request.user
        user_groups = user.group_set.all()

        if not user_groups.exists():
            return Response({
                "status": 404,
                "success": False,
                "message": "사용자는 어떤 그룹에도 속해 있지 않습니다.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

        evals = GroupEval.objects.filter(
            week_start_date__date=prev_week_start_date,
            group_id__in=user_groups
        ).values('target_email__email') \
         .annotate(average_rating=Avg('rating'))

        if not evals:
            return Response({
                "status": 204,
                "success": True,
                "message": f"{prev_week_start_date} 주차의 평가 내역이 존재하지 않습니다.",
                "data": []
            }, status=status.HTTP_200_OK)

        results = [
            {
                "target_email": entry['target_email__email'],
                "average_rating": round(entry['average_rating'], 1)  # 소수점 1번째자리까지만 평점 계산
            } for entry in evals
        ]

        serializer = GroupEvalAverageSerializer(data=results, many=True)
        serializer.is_valid()

        return Response({
            "status": 200,
            "success": True,
            "message": "그룹원 평가 조회를 완료했습니다.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)