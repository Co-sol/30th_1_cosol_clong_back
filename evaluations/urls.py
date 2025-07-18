from django.urls import path
from .views import GroupEvalCreateView, GroupEvalAverageView


urlpatterns = [
    path('evaluations/', GroupEvalCreateView.as_view(), name='group-eval-create'),
    path('view/', GroupEvalAverageView.as_view(), name='group-eval-average'), 
]
