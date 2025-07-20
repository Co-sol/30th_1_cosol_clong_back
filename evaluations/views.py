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
from django.utils.dateparse import parse_date
from groups.models import Group
from checklists.models import Checklistitem

class GroupEvalCreateView(APIView):  # 그룹원 평가 진행
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

    def get(self, request, group_id):
        user = request.user

        if user.group_id != int(group_id):
            return Response({
                "status": 403,
                "success": False,
                "message": f"해당 그룹에 대한 접근 권한이 없습니다."
            }, status=status.HTTP_403_FORBIDDEN)

        today = datetime.today()
        last_sunday = today - timedelta(days=today.weekday() + 1)
        prev_week_start = last_sunday - timedelta(days=7)
        prev_week_start_date = prev_week_start.date()

        evals = GroupEval.objects.filter(
            week_start_date__date=prev_week_start_date,
            group_id=group_id
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
                "average_rating": round(entry['average_rating'], 1)
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



# 청소 평가 조회
class GroupLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        group_id = request.query_params.get("group_id")
        date_str = request.query_params.get("date")

        if not group_id or not date_str:
            return Response({
                "status": 400,
                "success": False,
                "errorCode": "NONE_QUERY_PARAMS",
                "message": f"group_id와 date 쿼리 파라미터가 모두 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({
                "status": 404,
                "success": False,
                "errorCode": "NONE_GROUP",
                "message": f"존재하지 않는 그룹입니다."
            }, status=status.HTTP_404_NOT_FOUND)
        
        date_obj = parse_date(date_str)
        if not date_obj:
            return Response({
                "status": 400,
                "success": False,
                "erroCode": "DATE_ERROR",
                "message": f"잘못된 날짜 형식입니다.(yyyy-mm-dd))"
            }, status= status.HTTP_400_BAD_REQUEST)
        
        group_members = group.members.all()

        logs = []
        for user in group_members:
            checklist_items = Checklistitem.objects.filter(
                email=user,
                complete_at__date = date_obj,
                status = 1
            )

            completed_count = checklist_items.count()  # 청소 완료 상태 
            eval_wait_count = ChecklistReview.objects.filter(   # 검토 대기 상태 
                checklist_item_id__in=checklist_items,
                review_status = 0
            ).count()

            logs.append({
                "user":{
                    "nickname": getattr(user, "name", ""), # 임시
                    "profile": getattr(user, "profile", "")  # 임시
                },
                "completed_count": completed_count,
                "Eval_wait_count": eval_wait_count
            })

            return Response({
                "status":200,
                "success": True,
                "message": "청소 평가 조회가 완료되었습니다.",
                "data":{
                    "date": date_str,
                    "logs": logs
                }
            }, status=status.HTTP_200_OK)