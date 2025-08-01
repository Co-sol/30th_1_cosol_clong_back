import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from users.models import User
from groups.models import Group
from evaluations.models import GroupEval
from django.db.models import Avg

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Calculates and updates user profile rankings based on weekly evaluations."

    def handle(self, *args, **options):
        self.stdout.write("Starting user profile update process...")

        # On Monday, calculate for the previous week (Sun-Sat)
        today = timezone.now().date()
        # Go back one day to ensure we are in the previous week
        last_week_day = today - timedelta(days=1)
        start_of_week = last_week_day - timedelta(days=last_week_day.weekday() + 1 if last_week_day.weekday() != 6 else 0)
        end_of_week = start_of_week + timedelta(days=6)

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
                        timezone.make_aware(timezone.datetime.combine(start_of_week, timezone.datetime.min.time())),
                        timezone.make_aware(timezone.datetime.combine(end_of_week, timezone.datetime.max.time()))
                    ]
                )

                if evaluations.exists():
                    average_rating = evaluations.aggregate(Avg("rating"))["rating__avg"]
                    member_evaluations.append({"user": member, "avg_rating": average_rating})
                else:
                    # If no evaluations, treat average rating as 0
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
                    user.profile = 4 - rank  # Rank from 4 (1st) down to 1 (4th)

                user.save()
                self.stdout.write(f"  Updated {user.email}'s profile to {user.profile}")

        self.stdout.write("User profile update process finished.")
