from django.contrib.auth import authenticate
from rest_framework import serializers
from users.models import User
from django.utils import timezone

class UserInfoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'password', 'name',
            'clean_sense', 'clean_type', 'clean_type_created_at',
            'profile', 'evaluation_status'
        )
        read_only_fields = ('id', 'clean_type_created_at')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False},
            'name': {'required': False},
            'clean_sense': {'required': False},
            'clean_type': {'required': False},
            'profile': {'required': False},
            'evaluation_status': {'required': False}
        }

    def update(self, instance, validated_data):
        updated = False

        if 'clean_type' in validated_data and validated_data['clean_type'] is not None:
            instance.clean_type_created_at = timezone.now()
            updated = True

        for attr, value in validated_data.items():
            if getattr(instance, attr) is not value:
                setattr(instance, attr, value)
                updated = True

        if updated:
            instance.save()

        return instance
