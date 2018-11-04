import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days, choice=None):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published), and
    choice to fill a relationship with Choice
    """
    time = timezone.now() + datetime.timedelta(days=days)
    q = Question.objects.create(question_text=question_text, pub_date=time)
    q.save()
    if choice:
        q.choice_set.create(choice_text=choice, votes=0)
    return q


class QuestionIndexViewTests(TestCase):
    def test_no_questions_index(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question_index(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(
            question_text="Past question.", days=-30, choice='Choice One')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question_index(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(
            question_text="Future question.", days=30, choice='Choice One')
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question_index(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(
            question_text="Past question.", days=-30, choice='Choice One')
        create_question(
            question_text="Future question.", days=30, choice='Choice Two')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions_index(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(
            question_text="Past question 1.", days=-30, choice='Choice One')
        create_question(
            question_text="Past question 2.", days=-5, choice='Choice Two')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_no_choices_index(self):
        """
        If no choices exist for a question, an appropriate message is displayed.
        """
        create_question(
            question_text="Question without choice", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_one_choice_index(self):
        """
        Questions with a choice are displayed on the
        index page.
        """
        create_question(
            question_text="Question with one choice", days=-5, choice='Choice One')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Question with one choice>']
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question_detail(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(
                question_text='Future question.', days=5, choice='Choice One')
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_detail(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(
                question_text='Past Question.', days=-5, choice='Choice One')
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


    def test_no_choices_detail(self):
        """
        If no choices exist for a question, an appropriate message is displayed.
        """
        no_choice = create_question(
            question_text="Question without choice", days=-5)
        response = self.client.get(reverse('polls:detail', args=(no_choice.id,)))
        self.assertEqual(response.status_code, 404)

    def test_one_choice_detail(self):
        """
        Questions with a choice are displayed on the
        detail page.
        """
        one_choice = create_question(
            question_text="Question with one choice", days=-5, choice='Choice One')
        response = self.client.get(reverse('polls:detail', args=(one_choice.id,)))
        self.assertEqual(
            response.context['question'], one_choice
        )

class QuestionResultsViewTests(TestCase):
    def test_future_question_results(self):
        """
        The result view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(
                question_text='Future question.', days=5, choice='Choice One')
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_results(self):
        """
        The result view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(
                question_text='Past Question.', days=-5, choice='Choice One')
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


    def test_no_choices_results(self):
        """
        If no choices exist for a question, an appropriate message is displayed.
        """
        no_choice = create_question(
            question_text="Question without choice", days=-5)
        response = self.client.get(reverse('polls:results', args=(no_choice.id,)))
        self.assertEqual(response.status_code, 404)

    def test_one_choice_results(self):
        """
        Questions with a choice are displayed on the
        results page.
        """
        one_choice = create_question(
            question_text="Question with one choice", days=-5, choice='Choice One')
        response = self.client.get(reverse('polls:results', args=(one_choice.id,)))
        self.assertEqual(
            response.context['question'],
            one_choice
        )
