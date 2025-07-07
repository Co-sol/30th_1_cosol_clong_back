from django.db import models

class Space(models.Model):
    space_parent_id = models.ForeignKey('self',null=True,blank=True, n_delete=models.CASCADE)
    #group.id = models.ForeignKey(Group, on_delete=models.CASCADE)
    space_name = models.CharField()
    space_type = models.IntegerField()

    def __str__(self):
        return self.space_name

class Item(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    start_x = models.IntegerField()
    start_y = models.IntegerField()
    end_x = models.IntegerField()
    end_y = models.IntegerField()

    def __str__(self):
        return self.item_name

class Checklist(models.Model):  
    item = models.ForeignKey(Item, on_delete=models.CASCADE)   
    checklist_count = models.IntegerField()
    def __str__(self):
        return self.item

class Checklistitem(models.Model):
     STATUS_CHOICES = (
        (0, '미완료'),
        (1, '기한 내 완료'),
        (2, '마감 기한 지남'),
    )
    checklist = models.ForeignKey(checklist, on_delete=models.CASCADE)  
    user = models.ForeignKey(users.User, to_field='email', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField(null=True, blank=True)  # 마감 기한
    complete_date = models.DateTimeField(null=True, blank=True) # 완료 날짜
    status = models.IntegerField(choices=STATUS_CHOICES, default=0) 

    def __str__(self):
        return self.title


    
