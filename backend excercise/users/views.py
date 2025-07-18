from django.shortcuts import render
from rest_framework import viewsets, permissions
from users.models import User
from users.serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    ordering_fields = ['id', 'email', 'name']
    ordering = ['id']
    filterset_fields = ['id', 'email', 'name']
    search_fields = ['email', 'name']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'admin':
            # Admin: see all users
            return User.objects.all()
        elif user.role == 'teacher':
            # Teachers see themselves and all students
            return User.objects.filter(Q(role='student') | Q(pk=user.pk))
        elif user.role == 'student':
            # Student: see only students
            return User.objects.filter(role='student')
        else:
            # Default: see nothing
            return User.objects.none()


class StudentRegistrationView(APIView):
    permission_classes = []  # Open registration
    serializer_class = UserSerializer

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
    serializer_class = UserSerializer

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
    serializer_class = UserSerializer

    def post(self, request):
        data = request.data.copy()
        data['role'] = 'admin'
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer  # <-- Add this

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer  # <-- Add this (for schema, even if not used directly)
    
    def delete(self, request, User_ID):
        try:
            user = User.objects.get(User_ID=User_ID)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({'detail': 'User deleted.'}, status=status.HTTP_204_NO_CONTENT)

