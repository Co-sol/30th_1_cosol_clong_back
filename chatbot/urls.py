# chatbot/urls.py
from django.urls import path
from .views import ChatbotAskView, ChatbotHistoryView

urlpatterns = [
    path("ask/", ChatbotAskView.as_view(), name="chatbot_ask"),
    path("history/", ChatbotHistoryView.as_view(), name="chatbot_history"),
]
