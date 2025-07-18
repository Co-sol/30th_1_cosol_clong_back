from django.db import models
from users.models import User
from groups.models import Group
from checklists.models import Checklistitem
# Create your models here.

class GroupEval(models.Model):
    evaluation_id = models.AutoField(primary_key=True)
    week_start_date = models.DateTimeField()
    rating = models.IntegerField()
    created_at = models.DateTimeField() # 평가 진행 날
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    target_email = models.ForeignKey(User, on_delete=models.CASCADE)

class ChecklistReview(models.Model):
    STATUS_CHOICES = (
        (0, '대기'),
        (1, '승인'),
        (2, '반려'),
    )
    review_id = models.AutoField(primary_key=True)
    review_status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    review_at = models.DateTimeField(null = True, blank=True)
    good_count = models.IntegerField()
    bad_count = models.IntegerField()
    email = models.ForeignKey(User, on_delete=models.CASCADE)   
    checklist_item_id = models.ForeignKey(Checklistitem)