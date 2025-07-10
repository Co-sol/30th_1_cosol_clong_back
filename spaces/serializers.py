from rest_framework import serializers
from .models import Space


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
