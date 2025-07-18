from rest_framework import serializers
from users.models import User
from groups.models import Group
from .models import GroupEval
from datetime import datetime, timedelta

class GroupEvalAverageSerializer(serializers.Serializer): # 평점 계산
    target_email = serializers.EmailField()
    average_rating = serializers.FloatField()

class EvaluationSerializer(serializers.Serializer):
    user_email = serializers.EmailField()
    rating = serializers.IntegerField(min_value=1, max_value=5)

class GroupEvalCreateSerializer(serializers.Serializer):
    created_at = serializers.DateField()
    evaluations = EvaluationSerializer(many=True)

    def validate_created_at(self, value):
        if value.weekday() != 6:  # 6 = Sunday
            raise serializers.ValidationError("평가는 일요일에만 가능합니다.")
        return value

    def create(self, validated_data):
        created_at = validated_data['created_at']
        evaluations = validated_data['evaluations']
        request_user = self.context['request'].user

        # 요청자의 그룹 가져오기
        group = Group.objects.get(members=request_user)

        # 주 시작일 계산 (월요일 기준)
        week_start = created_at - timedelta(days=created_at.weekday())

        created_evals = []
        for eval_data in evaluations:
            target_user = User.objects.get(email=eval_data['user_email'])

            eval_obj = GroupEval.objects.create(
                created_at=created_at,
                week_start_date=week_start,
                rating=eval_data['rating'],
                group_id=group,
                target_email=target_user
            )
            created_evals.append(eval_obj)

        return created_evals


class GroupEvalResponseSerializer(serializers.ModelSerializer):
    target_email = serializers.EmailField(source='target_email.email')

    class Meta:
        model = GroupEval
        fields = [
            'evaluation_id', 
            'week_start_date',
            'created_at', 
            'group_id',
            'target_email',
            'rating', 
        ]

