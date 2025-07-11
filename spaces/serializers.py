from rest_framework import serializers
from .models import Space


# 루트 안의 공간 생성
class SpaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = [
            "space_name",
            "space_type",
            "start_x",
            "start_y",
            "width",
            "height",
            "size",
            "direction",
            "group_id",
        ]


# 루트 공간 수정
class SpaceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = [
            "space_name",
            "space_type",
            "start_x",
            "start_y",
            "width",
            "height",
            "size",
            "direction",
        ]


# 공간 정보 응답
class SpaceResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = [
            "group_id",
            "space_id",
            "space_name",
            "space_type",
            "start_x",
            "start_y",
            "width",
            "height",
            "size",
            "direction",
        ]
