from rest_framework import serializers
from .models import Checklistitem, Checklist

class ChecklistitemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklistitem
        fields = "__all__"

class ChecklistCreateSerializer(serializers.ModelSerializer): # 생성 (checklist에 속한 항목)
    class Meta:
        model = Checklistitem
        fields = [
            'checklist_id', 
            'email', 
            'title', 
            'due_date',
            'unit_item',
        ]

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
    
