from django.urls import path
from .views import SpaceCreateView, SpaceRUDAPIView

urlpatterns = [
    path("<int:group_id>/create/", SpaceCreateView.as_view(), name="create_space"),
    path("<int:space_id>/", SpaceRUDAPIView.as_view(), name="ud_space"),
]
