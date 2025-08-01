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
import math

def update_user_profiles_by_group(group):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday() + 1 if today.weekday() != 6 else 0)
    end_of_week = start_of_week + timedelta(days=6)

    members = User.objects.filter(group=group)
    if not members.exists():
        return

    member_evaluations = []
    for member in members:
        evaluations = GroupEval.objects.filter(
            target_email=member,
            created_at__range=[
                timezone.make_aware(timezone.datetime.combine(start_of_week, timezone.datetime.min.time())),
                timezone.make_aware(timezone.datetime.combine(end_of_week, timezone.datetime.max.time()))
            ]
        )

        if evaluations.exists():
            average_rating = evaluations.aggregate(Avg("rating"))["rating__avg"]
            member_evaluations.append({"user": member, "avg_rating": average_rating})
        else:
            member_evaluations.append({"user": member, "avg_rating": 0})

    # Sort members by average rating in descending order
    sorted_members = sorted(member_evaluations, key=lambda x: x["avg_rating"], reverse=True)

    # Update profile rankings with tie handling
    rank = 0
    last_rating = -1
    for i, data in enumerate(sorted_members):
        user = data["user"]
        if data["avg_rating"] == 0:
            user.profile = 0
        else:
            if data["avg_rating"] != last_rating:
                rank = i
                last_rating = data["avg_rating"]
            user.profile = 4 - rank  # Rank from 4 (1st) down to 1 (4th)

        user.save()

class GroupEvalCreateView(APIView):  # 그룹원 평가 진행
    permission_classes = [IsAuthenticated]
    def post(self, request):
        group_id = request.user.group_id
        group = get_object_or_404(Group, pk=group_id)
        serializer = GroupEvalCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            evals = serializer.save()

             # User의 evaluation_status를 true로 업데이트
            request.user.evaluation_status = True
            request.user.save()

            # Update user profiles
            update_user_profiles_by_group(group)

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

# 해당 그룹원이 평가를 진행했는지 알려주는 로직
# user의 evaluation_status 반환    
class EvaluationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "status": 200,
            "success": True,
            "message": "유저의 평가 상태를 반환합니다.",
            "data": {
                "email": request.user.email,
                "evaluation_status": request.user.evaluation_status
            }
        }, status=status.HTTP_200_OK)


class GroupEvalAverageView(APIView):  # 평점 조회
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        group_id = user.group_id

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

        results = []
        for entry in evals:
            user = User.objects.get(email=entry['target_email__email'])

            # 주차 기준 범위 설정
            week_start = prev_week_start_date
            week_end = week_start + timedelta(days=6)

            weekly_completed_count = ChecklistReview.objects.filter(
                email=user,
                review_status=1,
                checklist_item_id__complete_at__date__range=[week_start, week_end]
            ).count()

            results.append({
                "target_email": entry['target_email__email'],
                "average_rating": round(entry['average_rating'], 1),
                "weekly_completed_count": weekly_completed_count,
                "user_info": UserSimpleSerializer(user).data,
            })

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

    def get(self, request):
        group_id = request.user.group_id
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
                "due_date": checklist_item.due_date,
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

# 유저별 날짜별 청소 항목 상태 리스트 조회
class UserChecklistStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        group_id = request.user.group_id
        date_str = request.data.get("date")
        email = request.data.get("email")

        if not date_str or not email:
            return Response({
                "status": 400,
                "success": False,
                "message": "date와 email 필드가 필요합니다"
            }, status=status.HTTP_400_BAD_REQUEST)

        date_obj = parse_date(date_str)
        if not date_obj:
            return Response({
                "status": 400,
                "success": False,
                "message": "날짜 형식이 잘못되었습니다. (yyyy-mm-dd)"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, group_id=group_id)
        except User.DoesNotExist:
            return Response({
                "status": 404,
                "success": False,
                "message": "해당 그룹에 속한 이메일 유저가 존재하지 않습니다."
            })

        # 공통 데이터 수집 함수
        def get_info(item, review=None):
            checklist = item.checklist_id
            space = checklist.space_id

            data = {
                "title": item.title,
                "complete_at": item.complete_at,
                "deadline": item.due_date,   # 마감기한 추가
                "location": {
                    "space": space.space_name,
                    "item": item.unit_item
                },
                "assignee": {
                    "id": item.email.id,
                    "name": item.email.name,
                    "email": item.email.email
                }
            }

            if review:
                data["review_id"] = review.review_id  # ✅ review_id 포함

            return data

        # 검토 대기
        pending_reviews = ChecklistReview.objects.filter(
            checklist_item_id__email=user,
            review_status=0
        ).select_related(
            "checklist_item_id__checklist_id__space_id",
            "checklist_item_id__email"
        )
        pending = [
            get_info(r.checklist_item_id, review=r)
            for r in pending_reviews
            if r.checklist_item_id.complete_at and r.checklist_item_id.complete_at.date() == date_obj
        ]

        # 청소 완료
        completed_reviews = ChecklistReview.objects.filter(
            checklist_item_id__email=user,
            review_status=1,
            review_at__date=date_obj
        ).select_related(
            "checklist_item_id__checklist_id__space_id",
            "checklist_item_id__email"
        )
        completed = [get_info(r.checklist_item_id) for r in completed_reviews]

        # 미션 실패
        rejected_reviews = ChecklistReview.objects.filter(
            checklist_item_id__email=user,
            review_status=2,
            review_at__date=date_obj
        ).select_related(
            "checklist_item_id__checklist_id__space_id",
            "checklist_item_id__email"
        )

        overdue_items = Checklistitem.objects.filter(
            email=user,
            complete_at__date=date_obj,
            status=2
        ).select_related(
            "checklist_id__space_id",
            "email"
        )

        failed = [get_info(r.checklist_item_id) for r in rejected_reviews] + [get_info(item) for item in overdue_items]

        return Response({
            "status": 200,
            "success": True,
            "message": "유저의 청소 기록이 조회되었습니다.",
            "data": {
                "user": UserSimpleSerializer(user).data,
                "date": date_str,
                "pending": pending,
                "completed": completed,
                "failed": failed
            }
        }, status=status.HTTP_200_OK)


# 청소 평가 진행
class ChecklistFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        group_id = request.user.group_id
        review_id = request.data.get("review_id") or request.query_params.get("review_id")
        
        if not review_id:
            return Response({
                "status": 400,
                "success": False,
                "message": "리뷰 ID가 필요합니다.",
                "data": None
            }, status=400)
    
        review = get_object_or_404(ChecklistReview, pk=review_id)
        feedback = request.data.get("feedback")

        assignee = review.checklist_item_id.email
        if assignee == request.user:
            return Response({
                "status": 403,
                "success": False,
                "message": "자신이 담당한 항목은 평가할 수 없습니다.",
                "data": None
            }, status=403)

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
        
        max_feedback_count = total_members - 1  # 평가 가능한 인원 수
        majority_count = math.ceil(max_feedback_count / 2)  # 과반수 기준

        if review.review_status == 0:
            if review.good_count >= majority_count:
                review.review_status = 1  # 승인
                review.review_at = timezone.now()
                status_updated = True
                new_status = review.review_status
            elif review.bad_count >= majority_count:
                review.review_status = 2  # 반려
                review.review_at = timezone.now()
                status_updated = True
                new_status = review.review_status

        # 평가 시점 변경
        if status_updated:
            checklist_item = review.checklist_item_id
            checklist_item.complete_at = review.review_at  # 또는 timezone.now()로 별도 기록
            checklist_item.save()

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

    def post(self, request):
        group_id = request.user.group_id
        date_str = request.data.get("date")

        if not date_str:
            return Response({
                "status": 400,
                "success": False,
                "errorCode": "NONE_DATE_FIELD",
                "message": "date 필드가 필요합니다."
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
        total_completed_count = 0  # 전체 완료 수 초기화

        for user in group_members:
            if date_obj == today:  # 오늘일 경우

                completed_count = ChecklistReview.objects.filter(
                    checklist_item_id__email=user,
                    review_status=1,  # 검토 결과, 승인(완료) 상태
                ).count()

                eval_wait_count = ChecklistReview.objects.filter(
                    checklist_item_id__email=user,
                    review_status=0,  # 검토 대기 상태
                ).count()

                logs.append({
                    "user": UserSimpleSerializer(user).data,
                    "completed_count": completed_count,  # 청소 완료
                    "eval_wait_count": eval_wait_count   # 검토 대기
                })

                total_completed_count += completed_count  # 누적합 계산

            else:
                # 과거 날짜인 경우
                completed_count = ChecklistReview.objects.filter(
                    checklist_item_id__email=user,
                    review_status=1,  # 검토 결과, 승인(완료) 상태
                    review_at__date=date_obj
                ).count()

                rejected_review_count = ChecklistReview.objects.filter(
                    checklist_item_id__email=user,
                    review_status=2,  # 검토 반려 상태
                    review_at__date=date_obj
                ).count()

                overdeadline_count = Checklistitem.objects.filter(
                    email=user,
                    complete_at__date=date_obj,
                    status=2   # 마감 기한 지난 상태
                ).count()
                
                failed_count = rejected_review_count + overdeadline_count

                logs.append({
                    "user": UserSimpleSerializer(user).data,
                    "completed_count": completed_count,  # 청소 완료
                    "failed_count": failed_count  # 미션 실패
                })

                total_completed_count += completed_count  # 과거일 경우에도 누적

        return Response({
            "status":200,
            "success": True,
            "message": "청소 평가 조회가 완료되었습니다.",
            "data":{
                "date": date_str,
                "logs": logs,
                "total_completed_count": total_completed_count
            }
        }, status=status.HTTP_200_OK)