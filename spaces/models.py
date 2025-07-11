from django.db import models
from groups.models import Group


# Create your models here.
class Space(models.Model):
    PUBLIC = 0
    PRIVATE = 1
    SPACE_TYPE_CHOICES = (
        (PUBLIC, "공용 공간"),
        (PRIVATE, "개인 공간"),
    )

    HORIZONTAL = 0
    VERTICAL = 1
    DIRECTION_CHOICES = (
        (HORIZONTAL, "가로"),
        (VERTICAL, "세로"),
    )

    space_id = models.AutoField(primary_key=True)
    space_name = models.CharField(max_length=255)
    space_type = models.IntegerField(choices=SPACE_TYPE_CHOICES)
    start_x = models.IntegerField()
    start_y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    size = models.IntegerField()
    direction = models.IntegerField(choices=DIRECTION_CHOICES)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="spaces", db_column="group_id"
    )


class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=255)
    start_x = models.IntegerField()
    start_y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    size = models.IntegerField()
    parent_space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="items",
        db_column="parent_space_id",
    )

    def __str__(self):
        return f"{self.item_name} (in space {self.parent_space.space_id})"
