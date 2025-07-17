from django.urls import path
from .views import (
    ChecklistCreateView,
    ChecklistDeleteView,
    ChecklistCompleteView,
    ChecklistSpaceView,
    PrioritySpaceView,
)

urlpatterns = [
    #  청소 구역 우선순위 조회
    path('spaces/top-checklists', PrioritySpaceView.as_view(), name='top3-spaces'),
    # 공간별 체크리스트 조회
    path('spaces/<int:space_id>/checklists', ChecklistSpaceView.as_view(), name='space-checklists'),
    # 체크리스트 항목 완료 처리
    path('checklist-items/<int:checklist_item_id>/complete/', ChecklistCompleteView.as_view(), name='checklist-item-complete'),
    # 체크리스트 항목 생성
    path('create/', ChecklistCreateView.as_view(), name='checklist-item-create'),
    # 체크리스트 항목 삭제
    path('checklist-items/<int:checklist_item_id>/', ChecklistDeleteView.as_view(), name='checklist-item-delete'),
]
