from multiprocessing import allow_connection_pickling
from tokenize import group
from django.contrib.auth import authenticate
from rest_framework import serializers
from users.models import User
from django.utils import timezone


class UserInfoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    group_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "name",
            "clean_sense",
            "clean_type",
            "clean_type_created_at",
            "profile",
            "evaluation_status",
            "group_id",
        )
        read_only_fields = ("id", "clean_type_created_at")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": False},
            "name": {"required": False},
            "clean_sense": {"required": False},
            "clean_type": {"required": False},
            "profile": {"required": False},
            "evaluation_status": {"required": False},
        }

    def get_group_id(self, obj):
        return obj.group_id

    def validate(self, attrs):
        for field in attrs.keys():
            if field == "":
                raise serializers.ValidationError("빈 필드명은 허용되지 않습니다.")

        allowed_fields = {
            "name",
            "clean_sense",
            "clean_type",
            "profile",
            "evaluation_status",
        }
        for field in attrs.keys():
            if field not in allowed_fields:
                raise serializers.ValidationError(
                    f"'{field}' 필드는 수정할 수 없습니다."
                )

        return attrs

    def validate_name(self, value):
        if value is not None and value.strip() == "":
            raise serializers.ValidationError("이름은 빈 값일 수 없습니다.")
        return value

    def validate_clean_sense(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError(
                "청소 민감도는 0~100 사이의 값이어야 합니다."
            )
        return value

    def update(self, instance, validated_data):
        updated = False

        if (
            "clean_type" in validated_data
            and validated_data["clean_type"] != instance.clean_type
        ):
            instance.clean_type_created_at = timezone.now()
            updated = True

        for attr, value in validated_data.items():
            if getattr(instance, attr) is not value:
                setattr(instance, attr, value)
                updated = True

        if updated:
            instance.save()

        return instance
