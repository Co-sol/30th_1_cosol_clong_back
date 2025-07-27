from rest_framework import serializers
from .models import Checklistitem, Checklist
from users.models import User  # User 모델 import

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'name',
            'profile'
        ]

class ChecklistitemSerializer(serializers.ModelSerializer):
    user_info = UserSimpleSerializer(source='email', read_only=True)
    email = serializers.SerializerMethodField()

    class Meta:
        model = Checklistitem
        fields = [
            'checklist_item_id',
            'checklist_id',
            'email',
            'title',
            'due_date',
            'unit_item',
            'status',
            'complete_at',
            'user_info'
        ]

    def get_email(self, obj):
        return obj.email.email  # email 필드의 실제 이메일 주소 반환

class ChecklistCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()  # 이메일을 문자열로 받음

    class Meta:
        model = Checklistitem
        fields = [
            'checklist_id', 
            'email', 
            'title', 
            'due_date',
            'unit_item',
        ]
        extra_kwargs = {  # Null처리
            'unit_item': {'required': False, 'allow_null': True},
        }

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("해당 이메일 사용자를 찾을 수 없습니다.")
        return value


class Checklist_view_Serializer(serializers.ModelSerializer):   #조회
    checklist_items = ChecklistitemSerializer(many=True, read_only=True)
    class Meta:
        model = Checklist
        fields = [
            'checklist_id',
            'total_count',
            'completed_count',
            'checklist_items',
        ]

class Checklist_complete_Serializer(serializers.ModelSerializer): # 완료
    class Meta:
        model = Checklistitem
        fields = [
            'checklist_item_id',
            'status',
            "complete_at"
        ]
    
