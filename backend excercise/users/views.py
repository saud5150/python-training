from django.shortcuts import render
from rest_framework import viewsets, permissions
from users.models import User
from users.serializers import UserSerializer

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