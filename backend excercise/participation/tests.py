from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from users.models import User
from quizzes.models import Subject, Quiz, Question
from participation.models import UserQuiz, UserAnswer

# Create your tests here.

class UserAnswerPermissionsTest(APITestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(email='admin@example.com', name='Admin', password='adminpass', role='admin')
        self.teacher = User.objects.create_user(email='teacher@example.com', name='Teacher', password='teacherpass', role='teacher')
        self.student1 = User.objects.create_user(email='student1@example.com', name='Student1', password='studentpass1', role='student')
        self.student2 = User.objects.create_user(email='student2@example.com', name='Student2', password='studentpass2', role='student')
        # Create subject, quiz, question
        self.subject = Subject.objects.create(Name='Math')
        self.quiz = Quiz.objects.create(Title='Quiz1', Description='Desc', Subject_ID=self.subject)
        self.question = Question.objects.create(Quiz_ID=self.quiz, Question_Text='2+2?', Correct_Answer='4')
        # Create UserQuiz for each student
        self.user_quiz1 = UserQuiz.objects.create(User_ID=self.student1, Quiz_ID=self.quiz, Score=0, Total_Questions=1, Total_Correct=0, Started_At='2023-01-01T00:00:00Z')
        self.user_quiz2 = UserQuiz.objects.create(User_ID=self.student2, Quiz_ID=self.quiz, Score=0, Total_Questions=1, Total_Correct=0, Started_At='2023-01-01T00:00:00Z')

    def get_token(self, user, password):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'email': user.email, 'password': password})
        return response.data['access']

    def auth_client(self, user, password):
        client = APIClient()
        token = self.get_token(user, password)
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        return client

    def test_student_can_only_create_own_useranswer(self):
        url = reverse('useranswer-list')
        # Student1 can create answer for their own UserQuiz
        client = self.auth_client(self.student1, 'studentpass1')
        resp = client.post(url, {'User_Quiz_ID': str(self.user_quiz1.User_Quiz_Id), 'Question_ID': str(self.question.Question_ID), 'Answer_Text': '4'})
        self.assertEqual(resp.status_code, 201)
        # Student1 cannot create answer for Student2's UserQuiz
        resp = client.post(url, {'User_Quiz_ID': str(self.user_quiz2.User_Quiz_Id), 'Question_ID': str(self.question.Question_ID), 'Answer_Text': '4'})
        self.assertEqual(resp.status_code, 403)

    def test_student_can_only_see_own_answers(self):
        # Create answers for both students
        UserAnswer.objects.create(User_Quiz_ID=self.user_quiz1, Question_ID=self.question, Answer_Text='4', Is_Correct=True)
        UserAnswer.objects.create(User_Quiz_ID=self.user_quiz2, Question_ID=self.question, Answer_Text='3', Is_Correct=False)
        url = reverse('useranswer-list')
        client = self.auth_client(self.student1, 'studentpass1')
        resp = client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(str(resp.data[0]['User_Quiz_ID']), str(self.user_quiz1.User_Quiz_Id))

    def test_admin_and_teacher_can_see_all_answers(self):
        UserAnswer.objects.create(User_Quiz_ID=self.user_quiz1, Question_ID=self.question, Answer_Text='4', Is_Correct=True)
        UserAnswer.objects.create(User_Quiz_ID=self.user_quiz2, Question_ID=self.question, Answer_Text='3', Is_Correct=False)
        url = reverse('useranswer-list')
        for user, pwd in [(self.admin, 'adminpass'), (self.teacher, 'teacherpass')]:
            client = self.auth_client(user, pwd)
            resp = client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.data), 2)
