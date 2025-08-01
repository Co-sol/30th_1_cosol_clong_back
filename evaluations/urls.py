from django.urls import path
from .views import (
    GroupEvalCreateView, 
    GroupEvalAverageView,
    ChecklistFeedbackView,
    GroupLogView,
    PendingReviewListView,
    UserChecklistStatusView,
    EvaluationStatusView
)

urlpatterns = [
    path('evaluation/', GroupEvalCreateView.as_view(), name='group-eval-create'),
    path('evaluation-view/', GroupEvalAverageView.as_view(), name='group-eval-average'), 
    path('logs-feedback/', ChecklistFeedbackView.as_view(), name='feedback'),
    path('logs/', GroupLogView.as_view(), name='log-view'),
    path('logs-pending/', PendingReviewListView.as_view()),
    path('logs-list/', UserChecklistStatusView.as_view()),
    path('evaluation-status/', EvaluationStatusView.as_view()),
]
