from rest_framework import serializers
from users.models import User
from groups.models import Group
from .models import GroupEval
from datetime import timedelta
from checklists.models import Checklistitem

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'name',
            'profile',
            'clean_type'  
        ]

class GroupEvalAverageSerializer(serializers.Serializer): # 평점 계산
    target_email = serializers.EmailField()
    average_rating = serializers.FloatField()
    user_info = UserSimpleSerializer()  # 👈 추가

class EvaluationSerializer(serializers.Serializer):
    user_email = serializers.EmailField()
    rating = serializers.IntegerField(min_value=0, max_value=5)

class GroupEvalCreateSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", input_formats=["%Y-%m-%dT%H:%M:%S"])  # 시간 포함 필수
    evaluations = EvaluationSerializer(many=True)

    def validate_created_at(self, value):
        if value.weekday() != 6:  # 일요일만 허용
            raise serializers.ValidationError("평가는 일요일에만 가능합니다.")
        return value

    def create(self, validated_data):
        created_at = validated_data['created_at']
        evaluations = validated_data['evaluations']
        request_user = self.context['request'].user

        # 요청자의 그룹
        group = Group.objects.get(members=request_user)

        # 주 시작일: 월요일
        week_start = created_at - timedelta(days=created_at.weekday())

        created_evals = []
        for eval_data in evaluations:
            target_user = User.objects.get(email=eval_data['user_email'])

            eval_obj = GroupEval.objects.create(
                created_at=created_at,
                week_start_date=week_start,
                rating=eval_data['rating'],
                group_id=group,
                evaluator_email=request_user, 
                target_email=target_user
            )
            created_evals.append(eval_obj)

        return created_evals

class GroupEvalResponseSerializer(serializers.ModelSerializer):
    target_email = serializers.EmailField(source='target_email.email')
    evaluator_email = serializers.EmailField(source='evaluator_email.email')  # ← 추가
    target_user_info = UserSimpleSerializer(source='target_email', read_only=True)
    
    class Meta:
        model = GroupEval
        fields = [
            'evaluation_id', 
            'week_start_date',
            'created_at', 
            'group_id',
            'evaluator_email', 
            'target_email',
            'rating', 
            'target_user_info'
        ]


class ChecklistFeedbackSerializer(serializers.Serializer):  # 청소 평가
    feedback = serializers.ChoiceField(choices=["good", "bad"])

class ChecklistItemPendingReviewSerializer(serializers.ModelSerializer):
    space_name = serializers.CharField(source='checklist_id.space_id.space_name')
    item_name = serializers.CharField(source='unit_item')
    complete_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False)

    class Meta:
        model = Checklistitem
        fields = [
            'checklist_item_id', 
            'title', 
            'space_name', 
            'item_name', 
            'complete_at'
            ]
