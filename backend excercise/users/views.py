from django.shortcuts import render
from rest_framework import viewsets, permissions
from users.models import User
from users.serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsAdmin

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'User_ID'
    ordering_fields = ['User_ID', 'email', 'name']
    ordering = ['User_ID']
    filterset_fields = ['User_ID', 'email', 'name']
    search_fields = ['email', 'name']


class StudentRegistrationView(APIView):
    permission_classes = []  # Open registration

    def post(self, request):
        data = request.data.copy()
        data['role'] = 'student'
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherRegistrationView(APIView):
    permission_classes = [IsAdmin]  # Only admins can create teachers

    def post(self, request):
        data = request.data.copy()
        data['role'] = 'teacher'
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminRegistrationView(APIView):
    permission_classes = [IsAdmin]  # Only admins can create admins

    def post(self, request):
        data = request.data.copy()
        data['role'] = 'admin'
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

