import email
from email import message
from math import e
from rest_framework import serializers
from .models import Space, Item
from users.models import User
from checklists.models import Checklist


class ChecklistIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklist
        fields = ["checklist_id", "space_id"]


# 루트 안의 공간 생성
class SpaceCreateSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = Space
        fields = [
            "space_name",
            "space_type",
            "owner_email",
            "start_x",
            "start_y",
            "width",
            "height",
            "size",
            "direction",
            "group_id",
        ]

    def validate(self, data):
        owner_email = data.pop("owner_email", None)
        if data.get("space_type") == 1:
            try:
                owner = User.objects.get(email=owner_email)
                data["owner"] = owner
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "해당 이메일의 사용자가 존재하지 않습니다"
                )
        return data


# 루트 안의 공간 수정
class SpaceUpdateSerializer(serializers.ModelSerializer):
    owner_email = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = [
            "space_name",
            "space_type",
            "owner_email",
            "start_x",
            "start_y",
            "width",
            "height",
            "size",
            "direction",
        ]

    def get_owner_email(self, obj):
        return obj.owner.email if obj.owner else None

    def update(self, instance, validated_data):
        owner_email = self.initial_data.get("owner_email")
        if owner_email:
            try:
                instance.owner = User.objects.get(email=owner_email)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "success": False,
                        "errorCode": "USER_NOT_FOUND",
                        "message": "해당 이메일의 사용자가 존재하지 않습니다.",
                    }
                )

        # 나머지 필드들 처리
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# 공간 정보 응답
class SpaceResponseSerializer(serializers.ModelSerializer):
    checklist_id = serializers.SerializerMethodField()
    owner_email = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = [
            "group_id",
            "space_id",
            "space_name",
            "space_type",
            "owner_email",
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

    def get_owner_email(self, obj):
        return obj.owner.email if obj.owner else None


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
            "size",
            "direction",
            "parent_space_id",
        ]


class SpaceInfoSerializer(serializers.ModelSerializer):
    items = ItemInfoSerializer(many=True, read_only=True)
    owner_email = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = [
            "space_id",
            "space_name",
            "space_type",
            "owner_email",
            "start_x",
            "start_y",
            "width",
            "height",
            "size",
            "direction",
            "items",
        ]

    def get_owner_email(self, obj):
        return obj.owner.email if obj.owner else None
