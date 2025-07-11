from django.db import models
from users.models import User
from spaces.models import Space, Item


class Checklist(models.Model):  
    item = models.ForeignKey(Item, on_delete=models.CASCADE)   
    checklist_count = models.IntegerField()
    def __str__(self):
        return str(self.item)

class Checklistitem(models.Model):
    STATUS_CHOICES = (
        (0, '미완료'),
        (1, '기한 내 완료'),
        (2, '마감 기한 지남'),
    )
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)  
    user = models.ForeignKey(User, to_field='email', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField(null=True, blank=True)  # 마감 기한
    complete_date = models.DateTimeField(null=True, blank=True) # 완료 날짜
    status = models.IntegerField(choices=STATUS_CHOICES, default=0) 

    def __str__(self):
        return self.title