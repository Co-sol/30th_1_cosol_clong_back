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
    UserSimpleSerializer,
    ChecklistItemPendingReviewSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from groups.models import Group
from checklists.models import Checklistitem
from datetime import date as date_class
from users.models import User

class GroupEvalCreateView(APIView):  # 그룹원 평가 진행
    permission_classes = [IsAuthenticated]
    def post(self, request,group_id):
        group = get_object_or_404(Group, pk=group_id)
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
            "message": f"유효성 검사를 실패했습니다.",
            "errors": serializer.errors # 디버깅용
        }, status=status.HTTP_400_BAD_REQUEST)

class GroupEvalAverageView(APIView):  # 평점 조회
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        user = request.user

        if user.group_id != int(group_id):
            return Response({
                "status": 403,
                "success": False,
                "message": "해당 그룹에 대한 접근 권한이 없습니다."
            }, status=status.HTTP_403_FORBIDDEN)

        today = datetime.today()

        # 이번 주 월요일
        this_monday = today - timedelta(days=today.weekday())
        # 지난 주 월요일
        last_monday = this_monday - timedelta(days=7)
        prev_week_start_date = last_monday.date()

        # 이번 주 일요일
        this_sunday = this_monday + timedelta(days=6)

        # 평가 조회는 일요일 이후에만 가능
        if today.date() < this_sunday.date():
            return Response({
                "status": 400,
                "success": False,
                "message": f"평가는 매주 일요일에 진행되므로, {this_sunday.date()} 이후에 평가 결과를 조회할 수 있습니다.",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        # 지난주 평가 내역을 기준으로 target_email별 평균 평점 계산
        evals = GroupEval.objects.filter(
            week_start_date__date=prev_week_start_date,
            group_id=group_id
        ).values('target_email__email') \
         .annotate(average_rating=Avg('rating'))

        if not evals.exists():
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
        serializer.is_valid(raise_exception=True)

        return Response({
            "status": 200,
            "success": True,
            "message": "그룹원 평가 조회를 완료했습니다.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

# 그룹 일지

# 청소 평가 리스트 조회
class PendingReviewListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        # 그룹 존재 여부 확인
        group = get_object_or_404(Group, pk=group_id)
        
        # 요청 유저가 해당 그룹 멤버인지 확인
        if not group.members.filter(id=request.user.id).exists():
            return Response({
                "status": 403,
                "success": False,
                "message": "해당 그룹의 멤버가 아닙니다.",
                "data": None
            }, status=403)
        
        # 그룹에 속한 checklist review 중 review_status=0 (평가 대기 상태) 조회
        reviews = ChecklistReview.objects.filter(
            checklist_item_id__checklist_id__space_id__group_id=group_id,
            review_status=0
        ).select_related(
            'checklist_item_id',
            'checklist_item_id__checklist_id',
            'checklist_item_id__checklist_id__space_id',
            'email'  # 담당자 (User 모델 FK)
        )

        data = []
        for review in reviews:
            checklist_item = review.checklist_item_id
            checklist = checklist_item.checklist_id
            space = checklist.space_id

            data.append({
                "review_id": review.review_id,
                "assignee": {
                    "id": review.email.id,
                    "email": review.email.email,
                    "name": review.email.name, 
                },
                "title": checklist_item.title,
                "complete_at": checklist_item.complete_at,
                "location": {
                    "space": space.space_name,
                    "item": checklist_item.unit_item
                }
            })
        
        return Response({
            "status": 200,
            "success": True,
            "message": "평가 대기 리뷰 목록입니다.",
            "data": data
        }, status=200)


# 청소 평가 진행
class ChecklistFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id, review_id):
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

        # group_id 검증 (ID 직접 비교)
        actual_group_id = review.checklist_item_id.checklist_id.space_id.group_id  

        if actual_group_id != group_id:
            return Response({
                "status": 403,
                "success": False,
                "message": f"리뷰 ID가 해당 그룹 ID에 속하지 않습니다.",
                "data": None
            }, status=403)

        # group 객체 가져오기
        group = review.checklist_item_id.checklist_id.space_id.group

        group_members = group.members.all()
        total_members = group_members.count()

        total_feedback = review.good_count + review.bad_count

        if review.review_status == 0 and total_feedback >= total_members:
            if review.good_count >= review.bad_count:
                review.review_status = 1  # 승인
            else:
                review.review_status = 2  # 반려
            review.review_at = timezone.now()
            status_updated = True
            new_status = review.review_status

        review.save()

        # 관련 정보 가져오기
        checklist_item = review.checklist_item_id
        space_name = checklist_item.checklist_id.space_id.space_name
        item_name = checklist_item.unit_item
        complete_at = checklist_item.complete_at

        return Response({
            "status": 200,
            "success": True,
            "message": "청소 평가가 완료되었습니다.",
            "data": {
                "good_count": review.good_count,
                "bad_count": review.bad_count,
                "status_updated": status_updated,
                "new_status": new_status,
                "location": {
                    "space": space_name,
                    "item": item_name
                },
                "complete_at": complete_at,
            }
        }, status=status.HTTP_200_OK)
    

# 청소 평가 기록 조회
class GroupLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        date_str = request.query_params.get("date")

        if not date_str:
            return Response({
                "status": 400,
                "success": False,
                "errorCode": "NONE_QUERY_PARAMS",
                "message": "date 쿼리 파라미터가 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(group_id=group_id)
        except Group.DoesNotExist:
            return Response({
                 "status": 404,
                "success": False,
                "errorCode": "NONE_GROUP",
                "message": "존재하지 않는 그룹입니다."
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

        today = date_class.today()
        logs = []
        for user in group_members:
            if date_obj == today:
                checklist_items = Checklistitem.objects.filter(
                    email=user,
                    complete_at__date=date_obj,
                    status=1
                )

                completed_count = checklist_items.count()  # 검토 대기 상태
                eval_wait_count = ChecklistReview.objects.filter(
                    checklist_item_id__in=checklist_items,
                    review_status=0
                ).count()

                logs.append({
                    "user": UserSimpleSerializer(user).data,
                    "completed_count": completed_count,
                    "eval_wait_count": eval_wait_count
                })

            else:
                # 과거 날짜인 경우
                completed_review_count = ChecklistReview.objects.filter(
                    checklist_item_id__email=user,
                    review_status=1,  # 검토 결과, 승인(완료) 상태
                    review_at__date=date_obj
                ).count()

                rejected_review_count = ChecklistReview.objects.filter(
                    checklist_item_id__email=user,
                    review_status=2,  # 검토 결과, 반려 상태
                    review_at__date=date_obj
                ).count()

                logs.append({
                    "user": UserSimpleSerializer(user).data,
                    "completed_review_count": completed_review_count,
                    "rejected_review_count": rejected_review_count
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