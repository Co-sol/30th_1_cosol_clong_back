from django.urls import path
from .views import (
    Checklist_Group_View,
    Checklist_Item_View, 
    Checklist_Create_View,
    Checklist_Delete_View,
    Complete_Checklist_View
)
urlpatterns = [
    path('spaces/<int:space>/checklists/', Checklist_Group_View.as_view()),
    path('spaces/items/<int:item>/checklists/', Checklist_Item_View.as_view()),
    path('checklists/create/',Checklist_Create_View.as_view()),
    path('checklists/<int:pk>/complete/',Complete_Checklist_View.as_view()),
    path('checklists/<int:pk>/delete/',Checklist_Delete_View.as_view()),
]