from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from users.models import User
from quizzes.models import Subject, Quiz, Question

class QuizQuestionPermissionsTest(APITestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(email='admin@example.com', name='Admin', password='adminpass', role='admin')
        self.teacher = User.objects.create_user(email='teacher@example.com', name='Teacher', password='teacherpass', role='teacher')
        self.student = User.objects.create_user(email='student@example.com', name='Student', password='studentpass', role='student')
        # Create a subject and quiz
        self.subject = Subject.objects.create(Name='Math')
        self.quiz = Quiz.objects.create(Title='Quiz1', Description='Desc', Subject_ID=self.subject)
        self.question = Question.objects.create(Quiz_ID=self.quiz, Question_Text='2+2?', Correct_Answer='4')

    def get_token(self, user):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'email': user.email, 'password': 'adminpass' if user.role == 'admin' else 'teacherpass' if user.role == 'teacher' else 'studentpass'})
        return response.data['access']

    def auth_client(self, user):
        client = APIClient()
        token = self.get_token(user)
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        return client

    def test_quiz_permissions(self):
        url = reverse('quiz-list')
        detail_url = reverse('quiz-detail', args=[self.quiz.Quiz_ID])

        # Admin can create
        client = self.auth_client(self.admin)
        resp = client.post(url, {'Title': 'Q2', 'Description': 'D', 'Subject_ID': str(self.subject.Subject_ID)})
        self.assertEqual(resp.status_code, 201)

        # Teacher can create
        client = self.auth_client(self.teacher)
        resp = client.post(url, {'Title': 'Q3', 'Description': 'D', 'Subject_ID': str(self.subject.Subject_ID)})
        self.assertEqual(resp.status_code, 201)

        # Student cannot create
        client = self.auth_client(self.student)
        resp = client.post(url, {'Title': 'Q4', 'Description': 'D', 'Subject_ID': str(self.subject.Subject_ID)})
        self.assertEqual(resp.status_code, 403)

        # All can list
        for user in [self.admin, self.teacher, self.student]:
            client = self.auth_client(user)
            resp = client.get(url)
            self.assertEqual(resp.status_code, 200)

        # Only admin/teacher can update/delete
        for user, expected in [(self.admin, 200), (self.teacher, 200), (self.student, 403)]:
            client = self.auth_client(user)
            resp = client.patch(detail_url, {'Title': 'Updated'}, format='json')
            self.assertEqual(resp.status_code, expected if expected == 200 else 403)
            resp = client.delete(detail_url)
            if user.role == 'student':
                self.assertEqual(resp.status_code, 403)
            else:
                # Re-create for next test
                self.quiz = Quiz.objects.create(Title='Quiz1', Description='Desc', Subject_ID=self.subject)
                detail_url = reverse('quiz-detail', args=[self.quiz.Quiz_ID])

    def test_question_permissions(self):
        url = reverse('question-list')
        detail_url = reverse('question-detail', args=[self.question.Question_ID])

        # Admin can create
        client = self.auth_client(self.admin)
        resp = client.post(url, {'Quiz_ID': str(self.quiz.Quiz_ID), 'Question_Text': '3+3?', 'Correct_Answer': '6'})
        self.assertEqual(resp.status_code, 201)

        # Teacher can create
        client = self.auth_client(self.teacher)
        resp = client.post(url, {'Quiz_ID': str(self.quiz.Quiz_ID), 'Question_Text': '4+4?', 'Correct_Answer': '8'})
        self.assertEqual(resp.status_code, 201)

        # Student cannot create
        client = self.auth_client(self.student)
        resp = client.post(url, {'Quiz_ID': str(self.quiz.Quiz_ID), 'Question_Text': '5+5?', 'Correct_Answer': '10'})
        self.assertEqual(resp.status_code, 403)

        # All can list
        for user in [self.admin, self.teacher, self.student]:
            client = self.auth_client(user)
            resp = client.get(url)
            self.assertEqual(resp.status_code, 200)

        # Only admin/teacher can update/delete
        for user, expected in [(self.admin, 200), (self.teacher, 200), (self.student, 403)]:
            client = self.auth_client(user)
            resp = client.patch(detail_url, {'Question_Text': 'Updated'}, format='json')
            self.assertEqual(resp.status_code, expected if expected == 200 else 403)
            resp = client.delete(detail_url)
            if user.role == 'student':
                self.assertEqual(resp.status_code, 403)
            else:
                # Re-create for next test
                self.question = Question.objects.create(Quiz_ID=self.quiz, Question_Text='2+2?', Correct_Answer='4')
                detail_url = reverse('question-detail', args=[self.question.Question_ID])