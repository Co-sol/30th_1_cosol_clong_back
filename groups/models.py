from django.db import models


# Create your models here.
class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=255)
    group_rule = models.TextField(blank=True, null=True)
    group_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.group_name} ({self.group_id})"
