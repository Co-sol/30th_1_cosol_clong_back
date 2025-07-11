from django.urls import path
from .views import (
    Checklist_Group_View,
    Checklist_Item_View, 
    Checklist_Create_View,
    Checklist_Delete_View,
    Complete_Checklist_View,
    TopChecklistSpacesView
)
urlpatterns = [
    path('spaces/<int:space>/checklists/', Checklist_Group_View.as_view(), name='checklist_group_view'),
    path('spaces/items/<int:item>/checklists/', Checklist_Item_View.as_view(), name='checklist_item_view'),
    path('create/', Checklist_Create_View.as_view(), name='create_checklist'),
    path('<int:pk>/complete/', Complete_Checklist_View.as_view(), name='complete_checklist'),
    path('<int:pk>/delete/', Checklist_Delete_View.as_view(), name='delete_checklist'),
    path('spaces/top-incomplete/', TopChecklistSpacesView.as_view(), name='top-incomplete-spaces'),
]
