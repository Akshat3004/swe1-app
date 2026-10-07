from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from polls.models import Choice, Question


class Command(BaseCommand):
    help = 'Add sample polls if missing, preserving existing votes.'

    @transaction.atomic
    def handle(self, *args, **options):
        samples = {
            'Which programming language do you enjoy using most?': ['Python', 'Java', 'C++', 'JavaScript'],
            'Where do you prefer to study?': ['Library', 'Home', 'Coffee shop'],
        }
        for text, choices in samples.items():
            question, _ = Question.objects.get_or_create(
                question_text=text, defaults={'pub_date': timezone.now()}
            )
            for label in choices:
                Choice.objects.get_or_create(question=question, choice_text=label)
        self.stdout.write(self.style.SUCCESS('Sample polls are ready. Existing votes were kept.'))
