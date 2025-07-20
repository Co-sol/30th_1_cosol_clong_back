from rest_framework import serializers
from .models import Space, Item
from checklists.models import Checklist


class ChecklistIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklist
        fields = ["checklist_id", "space_id"]


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


# 루트 안의 공간 수정
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
    checklist_id = serializers.SerializerMethodField()

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
            "checklist_id",
        ]

    def get_checklist_id(self, obj):
        checklist = Checklist.objects.filter(space_id=obj).first()
        return checklist.checklist_id if checklist else None


# 아이템 생성
class ItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "item_name",
            "start_x",
            "start_y",
            "width",
            "height",
            "size",
            "direction",
            "parent_space_id",
        ]


# 아이템 수정
class ItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "item_name",
            "start_x",
            "start_y",
            "width",
            "height",
            "size",
            "direction",
        ]


# 아이템 정보 응답
class ItemResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "parent_space_id",
            "item_id",
            "item_name",
            "start_x",
            "start_y",
            "width",
            "height",
            "size",
            "direction",
        ]


# 공간 정보 응답용
class ItemInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "item_id",
            "item_name",
            "start_x",
            "start_y",
            "width",
            "height",
            "parent_space_id",
        ]


class SpaceInfoSerializer(serializers.ModelSerializer):
    items = ItemInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Space
        fields = [
            "space_id",
            "space_name",
            "space_type",
            "start_x",
            "start_y",
            "width",
            "height",
            "items",
        ]
