from pyexpat import model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from groups.models import Group
from users.models import User

DIRECTION_CHOICES = [("horizontal", "가로"), ("vertical", "세로")]
SIZE_CHOICES = [(1, "1배"), (2, "2배")]
SPACE_TYPE_CHOICES = [(0, "Public"), (1, "Private")]

# Create your models here.
class Space(models.Model):
    space_id = models.AutoField(primary_key=True)
    space_name = models.CharField(max_length=255)
    space_type = models.IntegerField(choices=SPACE_TYPE_CHOICES)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="private_spaces",
    )
    start_x = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9)]
    )
    start_y = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9)]
    )
    width = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(8)])
    height = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(6)]
    )
    size = models.IntegerField(choices=SIZE_CHOICES)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="spaces", db_column="group_id"
    )


class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=255)
    start_x = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9)]
    )
    start_y = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9)]
    )
    width = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    height = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    size = models.IntegerField(choices=SIZE_CHOICES)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    parent_space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="items",
        db_column="parent_space_id",
    )
