from django.urls import path
from .views import GroupEvalCreateView

urlpatterns = [
    path('evaluations/', GroupEvalCreateView.as_view(), name='group-eval-create')
]
