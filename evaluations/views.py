from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
from .models import GroupEval, ChecklistReview
from datetime import datetime, timedelta
from .serializers import (
    GroupEvalCreateSerializer, 
    GroupEvalResponseSerializer,
    GroupEvalAverageSerializer,
    ChecklistFeedbackSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

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

class GroupEvalAverageView(APIView):   # 평점 계산
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

# 그룹 일지
class ChecklistFeedbackView(APIView):  # 청소 평가
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        review = get_object_or_404(ChecklistReview, pk=review_id)
        feedback = request.data.get("feedback")

        serializer = ChecklistFeedbackSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": 400,
                "success": False,
                "message": "feedback 값은 'good' 또는 'bad'여야 합니다.",
                "data": None
            }, status=400)

        # 평가 반영
        if feedback == "good":
            review.good_count += 1
        else:
            review.bad_count += 1

        status_updated = False
        new_status = review.review_status

        # 전체 그룹원 수 가져오기
        group = review.checklist_item_id.checklist_id.space_id.group_id
        group_members = group.members.all()
        total_members = group_members.count()

        total_feedback = review.good_count + review.bad_count

        # 과반수 이상 평가 들어오면 상태 결정
        if review.review_status == 0 and total_feedback >= total_members:
            if review.good_count > review.bad_count:
                review.review_status = 1  # 승인
            else:
                review.review_status = 2  # 반려
            review.review_at = timezone.now()
            status_updated = True
            new_status = review.review_status

        review.save()

        return Response({
            "status": 200,
            "success": True,
            "message": "청소 평가가 완료되었습니다.",
            "data": {
                "good_count": review.good_count,
                "bad_count": review.bad_count,
                "status_updated": status_updated,
                "new_status": new_status
            }
        }, status=status.HTTP_200_OK)