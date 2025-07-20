from django.db import models
from users.models import User
from spaces.models import Space


class Checklist(models.Model):  
    checklist_id = models.AutoField(primary_key=True)
    total_count = models.IntegerField(null=True)
    completed_count = models.IntegerField(null=True)
    space_id = models.ForeignKey(Space, on_delete=models.CASCADE)

    def __str__(self):
        return self.space_id.space_name

class Checklistitem(models.Model):
    STATUS_CHOICES = (
        (0, '미완료'),
        (1, '기한 내 완료'),
        (2, '마감 기한 지남'),
    )
    checklist_item_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)  # 항목 제목
    due_date = models.DateTimeField()  # 마감 기한
    complete_at = models.DateTimeField(null=True, blank=True) # 완료 날짜
    status = models.IntegerField(choices=STATUS_CHOICES, default=0) 
    unit_item = models.CharField(max_length=255)
    checklist_id = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="checklist_items", null=True) 
    email = models.ForeignKey(User, on_delete=models.CASCADE) 
   
    def __str__(self):
        return self.title