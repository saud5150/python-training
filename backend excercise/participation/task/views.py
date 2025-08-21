from venv import logger
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import status
from base_view import BaseView
from participation.filters import TaskFilter
from participation.task.models import Task
from participation.permissions import IsAdminOrReadUpdate
from participation.task.serializers import TaskSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample

# Create your views here.

@extend_schema(
    tags=['Participation/ Task'],
    parameters=[

                OpenApiParameter(
            'type', 
            OpenApiTypes.STR, 
            description='Filter by task type',
            enum=['quiz', 'reminder', 'todo'],
            examples=[
                OpenApiExample('Quiz tasks', value='quiz'),
                OpenApiExample('Reminder tasks', value='reminder'),
                OpenApiExample('Todo tasks', value='todo'),
            ]
        ),
        # Basic filters
        OpenApiParameter('title', OpenApiTypes.STR, description='Filter by task title (contains)'),
        OpenApiParameter('description', OpenApiTypes.STR, description='Filter by task description (contains)'),
        OpenApiParameter('status', OpenApiTypes.STR, description='Filter by task status', 
                        enum=['pending', 'in_progress', 'completed', 'cancelled']),
        OpenApiParameter('priority', OpenApiTypes.STR, description='Filter by task priority',
                        enum=['low', 'medium', 'high', 'urgent']),
        
        # User filters
        OpenApiParameter('assigned_to', OpenApiTypes.UUID, description='Filter by assigned user ID'),
        
        # Date filters
        OpenApiParameter('created_after', OpenApiTypes.DATETIME, description='Filter tasks created after this date'),
        OpenApiParameter('created_before', OpenApiTypes.DATETIME, description='Filter tasks created before this date'),
        OpenApiParameter('due_after', OpenApiTypes.DATETIME, description='Filter tasks due after this date'),
        OpenApiParameter('due_before', OpenApiTypes.DATETIME, description='Filter tasks due before this date'),

        # Search and ordering
        OpenApiParameter('title', OpenApiTypes.STR, description='Search in title'),
        OpenApiParameter('description', OpenApiTypes.STR, description='Search in description'),
        OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by: title, -title, created_at, -created_at, due_date, -due_date, priority, -priority'),
        
        # Pagination
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number'),
        OpenApiParameter('page_size', OpenApiTypes.INT, description='Items per page'),
    ]
)
class TaskAPIView(BaseView):
    permission_classes = [IsAdminOrReadUpdate]
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'updated_at', 'due_date', 'priority', 'status']
    ordering = ['-created_at']


    def get(self, request, pk=None):
        try:
            if pk:
                task = get_object_or_404(Task, pk=pk)
                # Pass the task object, not serializer.data
                return self.send_successful_response(
                        data=task,
                        serializer_class=TaskSerializer,
                        description="Task retrieved successfully"
                )
            tasks = Task.objects.all()

            return self.send_successful_response(
                data=tasks,
                serializer_class=TaskSerializer,
                many=True,
                description="Tasks retrieved successfully"
            )
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
