from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Checklist,Checklistitem
from spaces.models import Space, Item
from .serializers import (
    Checklist_complete_Serializer,
    ChecklistSerializer,
    ChecklistItemCreateSerializer,
    Checklist_view_Serializer
)
from datetime import date, datetime
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, F


class Checklist_Group_View(APIView):  #조회(그룹)
    permission_classes = [IsAuthenticated]  #jwt 인증

    def get(self, request, space):
        update_status()  # 마감 상태 자동 갱신
        if not Space.objects.filter(space_id=space).exists():
            return Response({'error': 'Space not found'}, status=status.HTTP_404_NOT_FOUND)
        checklists = Checklist.objects.filter(item__parent_space_id=space)
        serializer = Checklist_view_Serializer(checklists,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class Checklist_Item_View(APIView):  #조회(개인)
    permission_classes = [IsAuthenticated]

    def get(self, request, item):
        update_status()  # 마감 상태 자동 갱신
        if not Item.objects.filter(item_id=item).exists():
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        checklists = Checklist.objects.filter(item_id=item)
        serializer = Checklist_view_Serializer(checklists,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class Checklist_Create_View(APIView): # 생성
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChecklistItemCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Checklist_Delete_View(APIView):  # 삭제
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk):
        checklist = get_object_or_404(Checklistitem, pk=pk)
        checklist.delete()
        return Response({"message":"삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

class Complete_Checklist_View(APIView): # 체크리스트 완료 처리
    permission_classes = [IsAuthenticated]

    def patch(self,request,pk):
        checklist = get_object_or_404(Checklistitem, pk=pk)
        status_val = request.data.get('status')
        
        if status_val not in [0,1,2]:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        
        checklist.status = status_val
        checklist.save()
        return Response({"id": checklist.id, "status": checklist.status}, status=200)

class TopChecklistSpacesView(APIView):  
    permission_classes = [IsAuthenticated]

    def get(self, request):
        top_spaces = top_checklist_spaces()
        return Response(top_spaces, status=status.HTTP_200_OK)

def update_status():  # 상태 판단 함수
    today = datetime.now()
    overdue_checklists = Checklistitem.objects.filter(
        status=0, 
        due_date__lt = today
    )
    updated_count = overdue_checklists.update(status=2)
    return updated_count


def top_checklist_spaces(): # top 3 체크리스트
    top_spaces = (
        Checklistitem.objects
        .filter(status=0)
        .values(
            space_id = F('checklist__item__parent_space__space_id'),
            space_name = F('checklist__item__parent_space__space_name')
        )
        .annotate(incomplete_count=Count('id'))
        .order_by('-incomplete_count')[:3]
    )
    return top_spaces


