from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


class PollFlowTests(TestCase):
    def setUp(self):
        self.question = Question.objects.create(question_text='Tea or coffee?', pub_date=timezone.now())
        self.choice = self.question.choice_set.create(choice_text='Tea')
        self.vote_url = reverse('polls:vote', args=[self.question.pk])

    def test_pages_and_root_redirect(self):
        self.assertRedirects(self.client.get('/'), reverse('polls:index'))
        self.assertContains(self.client.get(reverse('polls:index')), 'Tea or coffee?')
        self.assertContains(self.client.get(reverse('polls:detail', args=[self.question.pk])), 'Tea')
        self.assertContains(self.client.get(reverse('polls:results', args=[self.question.pk])), '0 votes')

    def test_vote_increments_and_refresh_does_not_repeat_it(self):
        response = self.client.post(self.vote_url, {'choice': self.choice.pk})
        results_url = reverse('polls:results', args=[self.question.pk])
        self.assertRedirects(response, results_url)
        self.client.get(results_url)
        self.client.get(results_url)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 1)

    def test_missing_invalid_and_other_question_choices_do_not_count(self):
        other = Question.objects.create(question_text='Another poll', pub_date=timezone.now())
        other_choice = other.choice_set.create(choice_text='Other answer')
        for payload in [{}, {'choice': 'invalid'}, {'choice': other_choice.pk}, {'choice': 999999}]:
            with self.subTest(payload=payload):
                response = self.client.post(self.vote_url, payload)
                self.assertContains(response, 'Please select one of the choices.')
        self.choice.refresh_from_db()
        other_choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 0)
        self.assertEqual(other_choice.votes, 0)

    def test_vote_rejects_get_and_unknown_question(self):
        self.assertEqual(self.client.get(self.vote_url).status_code, 405)
        self.assertEqual(self.client.post(reverse('polls:vote', args=[999999]), {'choice': self.choice.pk}).status_code, 404)

    def test_future_question_is_not_public(self):
        future = Question.objects.create(question_text='Tomorrow only', pub_date=timezone.now() + timedelta(days=1))
        self.assertNotContains(self.client.get(reverse('polls:index')), 'Tomorrow only')
        for name in ['polls:detail', 'polls:results']:
            self.assertEqual(self.client.get(reverse(name, args=[future.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('polls:vote', args=[future.pk])).status_code, 404)

    def test_seed_can_run_again_without_resetting_votes(self):
        call_command('seed_polls', stdout=StringIO())
        sample = Question.objects.get(question_text='Where do you prefer to study?')
        choice = sample.choice_set.first()
        choice.votes = 3
        choice.save()
        before = Question.objects.count()
        call_command('seed_polls', stdout=StringIO())
        choice.refresh_from_db()
        self.assertEqual(choice.votes, 3)
        self.assertEqual(Question.objects.count(), before)
