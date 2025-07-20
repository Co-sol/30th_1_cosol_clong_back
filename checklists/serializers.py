from rest_framework import serializers
from .models import Checklistitem, Checklist

class ChecklistitemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklistitem
        fields = "__all__"


from users.models import User  # User 모델 import

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

    def validate_email(self, value):
        try:
            return User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("해당 이메일 사용자를 찾을 수 없습니다.")


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
    
