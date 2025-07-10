from django.urls import path
from .views import SpaceCreateView

urlpatterns = [
    path("<int:group_id>/create/", SpaceCreateView.as_view(), name="create_space"),
]
