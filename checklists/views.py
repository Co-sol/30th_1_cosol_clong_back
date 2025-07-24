from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Checklist,Checklistitem
from spaces.models import Space
from .serializers import ( 
    Checklist_view_Serializer, 
    ChecklistCreateSerializer,
    ChecklistitemSerializer,
    Checklist_complete_Serializer,
    UserSimpleSerializer
)
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count
from evaluations.models import ChecklistReview

class ChecklistCreateView(APIView):  # 생성
    permission_classes = [IsAuthenticated]  # 토큰 인증

    def post(self, request):
        #update_expired_items()  # 자동 마감 기한 처리
        serializer = ChecklistCreateSerializer(data=request.data)

        if not serializer.is_valid():  # 입력값 오류
            return Response({
                "success": False,
                "errorCode": "MISSING_REQUIRED_FIELDS",
                "message": f"title, due_date, checklist_id는 필수입니다.",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        checklist_id = serializer.validated_data['checklist_id']
        user = serializer.validated_data['email']

        # 체크리스트 존재 확인
        checklist = Checklist.objects.filter(pk=checklist_id.pk).first()
        if not checklist:
            return Response({
                "success": False,
                "errorCode": "CHECKLIST_NOT_FOUND",
                "message": f"해당 checklist_id를 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 사용자 존재 확인
        if request.user != user:
            return Response({
                "success": False,
                "errorCode": "USER_NOT_FOUND",
                "message": f"해당 사용자를 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 체크리스트 항목 생성
        checklist_item = Checklistitem.objects.create(
            checklist_id = checklist_id,
            email=user,
            title=serializer.validated_data['title'],
            due_date=serializer.validated_data['due_date'],
            unit_item=serializer.validated_data.get('unit_item')  # None 허용
        )

        # total_count 증가
        checklist.total_count += 1
        checklist.save()

        response_serializer = ChecklistitemSerializer(checklist_item)
        
        return Response({
            "status": 200,
            "success": True,
            "message": f"체크리스트 항목이 성공적으로 생성되었습니다.",
            "data": response_serializer.data
        }, status=status.HTTP_200_OK)

class ChecklistSpaceView(APIView):  # 조회
    permission_classes = [IsAuthenticated]  # 토큰 인증

    def get(self, request, space_id):
        update_expired_items()  # 자동 마감 기한 처리

        # 공간 존재 여부 확인 
        space = Space.objects.filter(space_id=space_id).first()
        if not space:
            return Response({
                "success": False,
                "errorCode": "SPACE_NOT_FOUND",
                "message": f"해당 공간을 찾을 수 없습니다: space_id={space_id}"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 해당 공간의 체크리스트 가져오기
        checklists = Checklist.objects.filter(space_id=space)

        # 직렬화
        serializer = Checklist_view_Serializer(checklists, many=True) 

        return Response({
            "status": 200,
            "success": True,
            "message": f"체크리스트 목록 조회를 성공하였습니다.",
            "data" : serializer.data
        }, status=status.HTTP_200_OK)

class ChecklistDeleteView(APIView):  # 삭제
    permission_classes = [IsAuthenticated]  # 토큰 인증

    def delete(self, request, checklist_item_id):
        update_expired_items()  # 자동 마감 기한 처리
        # 항목 존재 여부 확인
        checklist_item = Checklistitem.objects.filter(checklist_item_id=checklist_item_id).first()
        if not checklist_item:
            return Response({
                "success": False,
                "errorCode": "CHECKLIST_ITEM_NOT_FOUND",
                "message": f"해당 체크리스트 항목을 찾을 수 없습니다: id={checklist_item_id}"
            }, status=status.HTTP_404_NOT_FOUND)

        # 연결된 checklist
        checklist = checklist_item.checklist_id

        # 삭제 전 카운트 업데이트
        checklist.total_count = max(checklist.total_count -1, 0)
        if checklist_item.status == 1:
            checklist.completed_count = max(checklist.completed_count -1,0)

        checklist.save() # DB 반영
        checklist_item.delete()  # 삭제

        return Response({
            "status": 200,
            "success": True,
            "message": f"체크리스트 항목이 성공적으로 삭제되었습니다."
        }, status=status.HTTP_200_OK)

class ChecklistCompleteView(APIView):  # 완료
    permission_classes = [IsAuthenticated]

    def patch(self, request, checklist_item_id):
        update_expired_items()  # 자동 마감 기한 처리
        # 항목 조회
        checklist_item = Checklistitem.objects.filter(checklist_item_id=checklist_item_id).first()
        if not checklist_item:
            return Response({
                "success": False,
                "errorCode": "CHECKLIST_ITEM_NOT_FOUND",
                "message": f"해당 체크리스트 항목을 찾을 수 없습니다: id={checklist_item_id}"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 권한 확인
        if checklist_item.email != request.user:
            return Response({
                "success": False,
                "errorCode": "NOT_AUTHORIZED",
                "message": f"해당 체크리스트를 완료 처리할 권한이 없습니다."
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 이미 완료된 경우
        if checklist_item.status == 1:
            return Response({
                "success": False,
                "errorCode": "ALREADY_COMPLETED",
                "message": f"이미 완료된 항목입니다: id={checklist_item_id}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 완료 처리
        checklist_item.status = 1
        checklist_item.complete_at = timezone.now()
        checklist_item.save()

        # completed_count 업데이트
        checklist= checklist_item.checklist_id
        checklist.completed_count += 1
        checklist.save()

        # 자동으로 ChecklistReview 생성
        ChecklistReview.objects.create(
            review_status=0,  # 대기 상태
            review_at=None,
            good_count=0,
            bad_count=0,
            email=request.user,  # 체크리스트 완료한 사용자
            checklist_item_id=checklist_item
        )

        serializer = Checklist_complete_Serializer(checklist_item)
        return Response({
            "status": 200,
            "success": True,
            "message": f"검토 대기 처리되었습니다.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
class PrioritySpaceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit_param = request.query_params.get('limit', '3')
        try:
            limit = int(limit_param)
            if limit < 1:
                raise ValueError
        except ValueError:
            return Response({
                "success": False,
                "errorCode": "INVALID_QUERY_PARAM",
                "message": "limit 값은 1이상 정수여야 합니다."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 미완료 항목들에 관해서만 카운트 진행
        space_count = (
            Checklistitem.objects
            .filter(status=0)
            .values('checklist_id__space_id','checklist_id__space_id__space_name')
            .annotate(checklist_item_count = Count('pk'))
            .order_by('-checklist_item_count')[:limit]
        )

        data = [
            {
                "space_id": space['checklist_id__space_id'],
                "space_name": space['checklist_id__space_id__space_name'],
                "checklist_item_count": space['checklist_item_count']
            }
            for space in space_count
        ]
        return Response({
            "status": 200,
            "success": True,
            "message": "청소 구역 우선순위 조회 성공",
            "data": data
        }, status=status.HTTP_200_OK)
    

# 마감 기한 지난 체크리스트 status 변경 -> 실시간 request시 반영 처리
def update_expired_items():
    now = timezone.now()
    expired_items = Checklistitem.objects.filter(status=0, due_date__lt=now)
    expired_items.update(status=2)
