from django.urls import path
from .views import ItemCreateView, ItemRUDAPIView, SpaceCreateView, SpaceRUDAPIView

urlpatterns = [
    path("<int:group_id>/create/", SpaceCreateView.as_view(), name="create_space"),
    path("<int:space_id>/", SpaceRUDAPIView.as_view(), name="ud_space"),
    path("items/<int:space_id>/create/", ItemCreateView.as_view(), name="create_item"),
    path("items/<int:item_id>/", ItemRUDAPIView.as_view(), name="ud_space"),
]
