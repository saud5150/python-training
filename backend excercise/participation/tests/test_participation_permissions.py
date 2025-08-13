from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS
from users.models import User
from participation.permissions import IsAdminOrReadOnly, AnswerPermission, IsAdminOrReadUpdate
from participation.models import Answer

class PermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        # Create users for each role
        self.admin_user = User.objects.create_user(email='admin@example.com', name='Admin User', password='pass', role='admin')
        self.teacher_user = User.objects.create_user(email='teacher@example.com', name='Teacher User', password='pass', role='teacher')
        self.student_user = User.objects.create_user(email='student@example.com', name='Student User', password='pass', role='student')
        self.other_student = User.objects.create_user(email='student2@example.com', name='Student Two', password='pass', role='student')
        self.anon_user = None

        # Create a dummy Answer object for object permission checks (link user_quiz_id.user_id to student_user)
        self.answer = Answer(
            id=1,
            user_quiz_id=None,  # Must link to object with user_quiz_id.user_id = student_user
            question_id=None,
            answer_text='Test answer',
            is_correct=True
        )
        # For object level tests, we will mock answer.user_quiz_id.user_id appropriately later

    # Helper to create requests with method and user
    def make_request(self, method, user):
        req = self.factory.generic(method, '/fake-url/')
        req.user = user if user else None
        return req

    # Tests for IsAdminOrReadOnly
    def test_is_admin_or_readonly_safe_methods_authenticated(self):
        perm = IsAdminOrReadOnly()
        for method in SAFE_METHODS:
            req = self.make_request(method, self.student_user)
            self.assertTrue(perm.has_permission(req, None))

    def test_is_admin_or_readonly_unsafe_methods_admin(self):
        perm = IsAdminOrReadOnly()
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            req = self.make_request(method, self.admin_user)
            self.assertTrue(perm.has_permission(req, None))

    def test_is_admin_or_readonly_unsafe_methods_non_admin(self):
        perm = IsAdminOrReadOnly()
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            for user in [self.teacher_user, self.student_user, self.anon_user]:
                req = self.make_request(method, user)
                self.assertFalse(perm.has_permission(req, None))

    # Tests for AnswerPermission
    def test_answer_permission_admin_teacher_all_methods(self):
        perm = AnswerPermission()
        for role_user in [self.admin_user, self.teacher_user]:
            for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                req = self.make_request(method, role_user)
                self.assertTrue(perm.has_permission(req, None))

    def test_answer_permission_student_safe_methods(self):
        perm = AnswerPermission()
        for method in ['GET', 'POST']:
            req = self.make_request(method, self.student_user)
            self.assertTrue(perm.has_permission(req, None))

    def test_answer_permission_student_unsafe_methods(self):
        perm = AnswerPermission()
        for method in ['PUT', 'PATCH', 'DELETE']:
            req = self.make_request(method, self.student_user)
            self.assertFalse(perm.has_permission(req, None))

    def test_answer_permission_anonymous_user(self):
        perm = AnswerPermission()
        req = self.make_request('GET', None)
        self.assertFalse(perm.has_permission(req, None))

    def test_answer_permission_object_level_admin_teacher(self):
        perm = AnswerPermission()
        for user in [self.admin_user, self.teacher_user]:
            req = self.make_request('GET', user)
            self.assertTrue(perm.has_object_permission(req, None, self.answer))

    # Tests for IsAdminOrReadUpdate
    def test_is_admin_or_readupdate_unsafe_methods_admin(self):
        perm = IsAdminOrReadUpdate()
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            req = self.make_request(method, self.admin_user)
            self.assertTrue(perm.has_permission(req, None))

    def test_is_admin_or_readupdate_object_permission_unsafe_admin(self):
        perm = IsAdminOrReadUpdate()
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            req = self.make_request(method, self.admin_user)
            self.assertTrue(perm.has_object_permission(req, None, None))
