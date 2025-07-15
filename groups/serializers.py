from dataclasses import field, fields
from pyexpat import model
from rest_framework import serializers
from checklists.models import Checklist, Checklistitem
from users.models import User
from groups.models import Group
from spaces.models import Space, Item
from .models import Group


# 유저 조회
class CheckUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name"]


# 그룹 생성
class GroupCreateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
    )

    class Meta:
        model = Group
        fields = ["group_name", "group_rule", "members"]

    # 한 번 더 memebers 검사
    def validate_members(self, emails):
        for email in emails:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    f"존재하지 않는 사용자입니다: {email}"
                )
            if user.group:
                raise serializers.ValidationError(
                    f"이미 다른 그룹에 속한 사용자입니다: {email}"
                )
        return emails

    # 생성
    def create(self, validated_data):
        members_emails = validated_data.pop("members", [])
        created_by = self.context["request"].user
        group = Group.objects.create(
            group_name=validated_data["group_name"],
            group_rule=validated_data.get("group_rule", ""),
        )

        created_by.group = group
        created_by.save()

        for email in members_emails:  # 멤버 초대
            user = User.objects.get(email=email)
            user.group = group
            user.save()
        return group


class ItemSerializer(serializers.ModelSerializer):
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


class SpaceSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

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


class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklistitem
        fields = ["title", "due_date", "status"]


class GroupInfoSeriazlier(serializers.ModelSerializer):
    spaces = SpaceSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ["group_name", "group_rule", "spaces"]


class GroupUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.EmailField(), write_only=True, required=False
    )

    class Meta:
        model = Group
        fields = ["group_name", "group_rule", "members"]

    def validate_members(self, emails):
        for email in emails:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    f"존재하지 않는 사용자입니다: {email}"
                )
            if user.group and user.group != self.instance:
                raise serializers.ValidationError(
                    f"이미 다른 그룹에 속한 사용자입니다: {email}"
                )
        return emails

    def update(self, instance, validated_data):
        instance.group_name = validated_data.get("group_name", instance.group_name)
        instance.group_rule = validated_data.get("group_rule", instance.group_rule)
        instance.save()

        member_emails = validated_data.get("members")
        if member_emails is not None:
            users = User.objects.filter(email__in=member_emails)

            for user in instance.members.all():
                user.group = None
                user.save()

            for user in users:
                user.group = instance
                user.save()

        return instance


class GroupMemberSerializer(serializers.ModelSerializer):
    checklists = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "clean_sense",
            "clean_type",
            "profile",
            "evaluation_status",
            "clean_type_created_at",
            "checklists",
        ]

    def get_checklists(self, user):
        checklistitems = Checklistitem.objects.filter(user=user, status=0)
        return ChecklistItemSerializer(checklistitems, many=True).data
