from django.urls import path
from .views import (
    GroupEvalCreateView, 
    GroupEvalAverageView,
    ChecklistFeedbackView,
    GroupLogView
)

urlpatterns = [
    path('<int:group_id>/evaluation/', GroupEvalCreateView.as_view(), name='group-eval-create'),
    path('<int:group_id>/view/', GroupEvalAverageView.as_view(), name='group-eval-average'), 
    path('<int:group_id>/<int:review_id>/logs/feedback/', ChecklistFeedbackView.as_view(), name='feedback'),
    path('<int:group_id>/logs?date=yyyy-mm-dd/', GroupLogView.as_view(), name='log-view'),
]
