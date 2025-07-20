from django.urls import path
from .views import (
    ChecklistCreateView,
    ChecklistDeleteView,
    ChecklistCompleteView,
    ChecklistSpaceView,
    PrioritySpaceView,
)

urlpatterns = [
    path('spaces/top-checklists/', PrioritySpaceView.as_view(), name='top3-spaces'),
    path('spaces/<int:space_id>/checklist/', ChecklistSpaceView.as_view(), name='space-checklists'),
    path('checklist-items/<int:checklist_item_id>/complete/', ChecklistCompleteView.as_view(), name='checklist-item-complete'),
    path('create/', ChecklistCreateView.as_view(), name='checklist-item-create'),
    path('checklist-items/<int:checklist_item_id>/delete/', ChecklistDeleteView.as_view(), name='checklist-item-delete'),
]
