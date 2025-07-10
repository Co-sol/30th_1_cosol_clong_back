from rest_framework import serializers
from users.models import User
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
