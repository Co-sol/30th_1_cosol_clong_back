from rest_framework import serializers
from users.models import User
from .models import Group


# 유저 조회
class CheckUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name"]

