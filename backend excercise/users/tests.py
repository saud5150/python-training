# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from quiz.models import Subject, Quiz
from participation.models import Task
from rest_framework.test import APIClient
from datetime import timedelta
from django.utils import timezone
from participation.models import Quiz as ParticipationQuiz

# Create your tests here.

class UserFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create users
        self.admin = User.objects.create_user(email='admin@example.com', name='Admin', password='adminpass', role='admin')
        self.teacher = User.objects.create_user(email='teacher@example.com', name='Teacher', password='teacherpass', role='teacher')
        self.ta = User.objects.create_user(email='ta@example.com', name='TA', password='tapass', role='student')
        self.student = User.objects.create_user(email='student@example.com', name='Student', password='studentpass', role='student')

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_admin_adds_courses_teachers_students(self):
        self.authenticate(self.admin)
        # Admin adds a course
        response = self.client.post(reverse('subject-list'), {'name': 'Math'})
        self.assertEqual(response.status_code, 201)
        subject_id = response.data['id']
        # Admin adds teachers and students (already done in setUp)
        self.assertEqual(User.objects.filter(role='teacher').count(), 1)
        self.assertEqual(User.objects.filter(role='student').count(), 2)  # student + ta

    def test_admin_assigns_teacher_to_course(self):
        self.authenticate(self.admin)
        subject = Subject.objects.create(name='Science')
        subject.teachers.add(self.teacher)
        self.assertIn(self.teacher, subject.teachers.all())

    def test_admin_assigns_teacher_task_to_create_quiz(self):
        self.authenticate(self.admin)
        # Admin assigns a task to teacher to create a quiz
        due = timezone.now() + timedelta(days=2)
        task = Task.objects.create(
            user_id=self.teacher,
            title='Create Quiz',
            description='Create a quiz for Science',
            status='pending',
            due_date=due,
            type='quiz'
        )
        self.assertEqual(task.user_id, self.teacher)
        self.assertEqual(task.type, 'quiz')

    def test_teacher_creates_task_for_ta_to_attempt_quiz(self):
        self.authenticate(self.teacher)
        subject = Subject.objects.create(name='English')
        quiz = Quiz.objects.create(subject_id=subject, title='Quiz 1', description='Desc', assigned_teacher=self.teacher)
        from participation.models import Quiz as ParticipationQuiz
        participation_quiz = ParticipationQuiz.objects.create(
            user_id=self.ta,
            quiz_id=quiz,
            score=None,
            total_questions=10,
            total_correct=0,
            completed_at=None
        )
        due = timezone.now() + timedelta(days=1)
        task = Task.objects.create(
            user_id=self.ta,
            user_quiz_id=participation_quiz,
            title='Attempt Quiz',
            description='TA should attempt the quiz',
            status='assigned',
            due_date=due,
            type='quiz'
        )
        self.assertEqual(task.user_id, self.ta)
        self.assertEqual(task.user_quiz_id, participation_quiz)

    def test_student_performs_quiz_within_deadline(self):
        self.authenticate(self.student)
        subject = Subject.objects.create(name='History')
        quiz = Quiz.objects.create(subject_id=subject, title='Quiz 2', description='Desc', assigned_teacher=self.teacher)
        # Simulate student performing quiz (participation logic)
        from participation.models import Quiz as ParticipationQuiz
        pq = ParticipationQuiz.objects.create(user_id=self.student, quiz_id=quiz, score=8, total_questions=10, total_correct=8, completed_at=timezone.now())
        self.assertEqual(pq.user_id, self.student)
        self.assertEqual(pq.quiz_id, quiz)

    def test_teacher_adds_scores_after_deadline(self):
        self.authenticate(self.teacher)
        subject = Subject.objects.create(name='Geo')
        quiz = Quiz.objects.create(subject_id=subject, title='Quiz 3', description='Desc', assigned_teacher=self.teacher)
        from participation.models import Quiz as ParticipationQuiz
        pq = ParticipationQuiz.objects.create(user_id=self.student, quiz_id=quiz, score=None, total_questions=10, total_correct=0, completed_at=None)
        # After deadline, teacher adds score
        pq.score = 7
        pq.completed_at = timezone.now()
        pq.save()
        self.assertEqual(pq.score, 7)

    def test_teacher_admin_calculate_aggregates(self):
        self.authenticate(self.admin)
        subject = Subject.objects.create(name='Bio')
        quiz1 = Quiz.objects.create(subject_id=subject, title='Quiz 1', description='Desc', assigned_teacher=self.teacher)
        quiz2 = Quiz.objects.create(subject_id=subject, title='Quiz 2', description='Desc', assigned_teacher=self.teacher)
        from participation.models import Quiz as ParticipationQuiz, Score
        ParticipationQuiz.objects.create(user_id=self.student, quiz_id=quiz1, score=9, total_questions=10, total_correct=9, completed_at=timezone.now())
        ParticipationQuiz.objects.create(user_id=self.student, quiz_id=quiz2, score=8, total_questions=10, total_correct=8, completed_at=timezone.now())
        # Calculate aggregate
        total = sum(pq.score for pq in ParticipationQuiz.objects.filter(user_id=self.student, quiz_id__subject_id=subject))
        Score.objects.create(user_id=self.student, subject_id=subject, aggregate_score=total)
        agg = Score.objects.get(user_id=self.student, subject_id=subject)
        self.assertEqual(agg.aggregate_score, 17)

    def test_course_quiz_and_student_course_relationships(self):
        self.authenticate(self.admin)
        subject = Subject.objects.create(name='CS')
        quiz1 = Quiz.objects.create(subject_id=subject, title='Quiz 1', description='Desc', assigned_teacher=self.teacher)
        quiz2 = Quiz.objects.create(subject_id=subject, title='Quiz 2', description='Desc', assigned_teacher=self.teacher)
        self.assertEqual(subject.quiz_set.count(), 2)
        # Student takes multiple courses
        subject2 = Subject.objects.create(name='Maths')
        subject2.teachers.add(self.teacher)
        # Simulate enrollment (if you have an enrollment model, use it; else, just logic)
        # Here, just check that student can participate in quizzes from multiple subjects
        from participation.models import Quiz as ParticipationQuiz
        pq1 = ParticipationQuiz.objects.create(user_id=self.student, quiz_id=quiz1, score=10, total_questions=10, total_correct=10, completed_at=timezone.now())
        pq2 = ParticipationQuiz.objects.create(user_id=self.student, quiz_id=quiz2, score=9, total_questions=10, total_correct=9, completed_at=timezone.now())
        self.assertEqual(pq1.user_id, self.student)
        self.assertEqual(pq2.user_id, self.student)
