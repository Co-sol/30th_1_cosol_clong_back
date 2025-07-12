from django.db import models
from django.conf import settings

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10)  # 'user' 또는 'assistant'
    message = models.TextField()
    order_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

