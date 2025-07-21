from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from users.models import User
from users.serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsAdmin, IsAdminOrTeacher
from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView

# Create your views here.


# List all users and create user (GET/POST /users/)
class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

# Retrieve, update, and delete a user (GET/PUT/PATCH/DELETE /users/<id>/)
class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'id'

# User Registration Views
class StudentRegistrationView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        serializer.save(role='student')

class TeacherRegistrationView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        serializer.save(role='teacher')

class AdminRegistrationView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        serializer.save(role='admin')

# User Profile View
class UserProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_object(self):
        return self.request.user
