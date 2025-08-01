from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = '모든 사용자의 evaluation_status를 0으로 초기화합니다.'

    def handle(self, *args, **kwargs):
        updated_count = User.objects.all().update(evaluation_status=0)
        self.stdout.write(self.style.SUCCESS(
            f'{updated_count}명의 유저 evaluation_status 초기화 완료'
        ))
