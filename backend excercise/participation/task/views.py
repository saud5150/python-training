from venv import logger
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import status
from base_view import BaseView
from participation.task.models import Task
from participation.permissions import IsAdminOrReadUpdate
from participation.task.serializers import TaskSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
# Create your views here.

@extend_schema(tags=['Participation/ Task'])
class TaskAPIView(BaseView):
    permission_classes = [IsAdminOrReadUpdate]
    serializer_class = TaskSerializer
    
    def get(self, request, pk=None):
        try:
            if pk:
                task = get_object_or_404(Task, pk=pk)
                
                serializer = TaskSerializer(task)
                return self.send_successful_response(serializer.data)
            tasks = Task.objects.all()
            serializer = TaskSerializer(tasks, many=True)
            return self.send_successful_response(serializer.data)
        except Http404:
            return Response(
                {'detail': 'Task not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while retrieving tasks")

    def post(self, request):
        try:
            serializer = TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_201_response(serializer.data)
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while creating the task")

    def put(self, request, pk):
        try:
            task = get_object_or_404(Task, pk=pk)
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.send_successful_response(serializer.data)
        except Http404:
            # Explicit 404 handling
            return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while updating the task")
        return self.send_bad_response(serializer.errors)

    def patch(self, request, pk):
        try:
            task = get_object_or_404(Task, pk=pk)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.send_successful_response(serializer.data)
        except Http404:
            # Explicit 404 handling
            return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while updating the task")
        return self.send_bad_response(serializer.errors)

    def delete(self, request, pk):
        try:
            task = get_object_or_404(Task, pk=pk)
            task.delete()
        except Http404:
            # Explicit 404 handling
            return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while deleting the task")
        return self.send_no_content_response()
