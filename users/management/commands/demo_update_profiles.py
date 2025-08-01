import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from users.models import User
from groups.models import Group
from evaluations.models import GroupEval
from django.db.models import Avg

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "(For Demo) Calculates and updates user profile rankings based on evaluations for a specific week."

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='The target date to run the calculation for (format: YYYY-MM-DD). The week of this date will be used.'
        )

    def handle(self, *args, **options):
        target_date_str = options['date']
        if not target_date_str:
            self.stdout.write(self.style.ERROR("Please provide a date using --date YYYY-MM-DD"))
            return

        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except ValueError:
            self.stdout.write(self.style.ERROR("Invalid date format. Please use YYYY-MM-DD"))
            return

        self.stdout.write(f"Starting user profile update process for the week of {target_date_str}...")

        # Calculate the week based on the provided date (Sunday as start of week)
        start_of_week = target_date - timedelta(days=target_date.weekday() + 1 if target_date.weekday() != 6 else 0)
        end_of_week = start_of_week + timedelta(days=6)

        self.stdout.write(f"Processing evaluations from {start_of_week} to {end_of_week}")

        groups = Group.objects.all()
        for group in groups:
            members = User.objects.filter(group=group)
            if not members.exists():
                continue

            self.stdout.write(f"Processing group: {group.group_name}")

            member_evaluations = []
            for member in members:
                evaluations = GroupEval.objects.filter(
                    target_email=member,
                    created_at__range=[
                        timezone.make_aware(datetime.combine(start_of_week, datetime.min.time())),
                        timezone.make_aware(datetime.combine(end_of_week, datetime.max.time()))
                    ]
                )

                if evaluations.exists():
                    average_rating = evaluations.aggregate(Avg("rating"))["rating__avg"]
                    member_evaluations.append({"user": member, "avg_rating": average_rating})
                else:
                    member_evaluations.append({"user": member, "avg_rating": 0})

            # Sort members by average rating in descending order
            sorted_members = sorted(member_evaluations, key=lambda x: x["avg_rating"], reverse=True)

            # Update profile rankings with tie handling
            rank = 0
            last_rating = -1
            for i, data in enumerate(sorted_members):
                user = data["user"]
                if data["avg_rating"] == 0:
                    user.profile = 0
                else:
                    if data["avg_rating"] != last_rating:
                        rank = i
                        last_rating = data["avg_rating"]
                    user.profile = 4 - rank

                user.save()
                self.stdout.write(f"  Updated {user.email}'s profile to {user.profile}")

        self.stdout.write(self.style.SUCCESS("User profile update process for demo finished."))
