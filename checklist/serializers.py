from rest_framework import serializers
from .models import Item,Checklistitem,Space

class UserSerializer(serializers.ModelSerializer):  # user 정보
    class Meta:
        model = users.User  # User 모델 가져오기
        fields = ['email','profile']

class SpaceSerializer(serializers.ModelSerializer):  # 공간 정보
    class Meta:
        model = Space  
        fields = ['space_name']

class ItemSerializer(serializers.ModelSerializer):  # 아이템 정보
    class Meta:
        model = Item  
        fields = ['item_name']

class ChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklist
        fields = ['item','space'] 

    def validate(self, data):
        item = data.get('item')
        space = data.get('space') 

        if not space:
            raise serializers.ValidationError("space는 필수입니다.")
        return data

class ChecklistItemCreateSerializer(serializers.ModelSerializer): # 생성 (checklist에 속한 항목)
    class Meta:
        model = Checklistitem
        fields = ['checklist', 'user', 'title', 'due_date']

class Checklist_view_Serializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    item = ItemSerializer(source='checklist.item',read_only=True)
    space = SpaceSerializer(source='checklist.item.space',read_only=True)

    class Meta:
        model = Checklistitem
        fields = ['id','user','title','due_date','status','item','space']

class Checklist_complete_Serializer(serializers.ModelSerializer): # 완료
    class Meta:
        model = Checklistitem
        fields = ['status']
