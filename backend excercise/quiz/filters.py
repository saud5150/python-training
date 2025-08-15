import django_filters
from django_filters import rest_framework as filters
from .models import Quiz, Question, Subject


class SubjectFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    name_exact = filters.CharFilter(field_name='name', lookup_expr='exact')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Subject
        fields = ['name']


class QuizFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    title_exact = filters.CharFilter(field_name='title', lookup_expr='exact')    
    subject_id = filters.UUIDFilter(field_name='subject_id__id')
    subject_name = filters.CharFilter(field_name='subject_id__name', lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    has_questions = filters.BooleanFilter(method='filter_has_questions')
    
    def filter_has_questions(self, queryset, name, value):
        if value:
            return queryset.filter(question__isnull=False).distinct()
        return queryset.filter(question__isnull=True).distinct()
    
    class Meta:
        model = Quiz
        fields = ['title', 'subject_id']


class QuestionFilter(filters.FilterSet):
    quiz_id = filters.UUIDFilter(field_name='quiz_id__id')
    quiz_title = filters.CharFilter(field_name='quiz_id__title', lookup_expr='icontains')
    subject_id = filters.UUIDFilter(field_name='quiz_id__subject_id__id')
    question_text = filters.CharFilter(field_name='question_text', lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Question
        fields = ['quiz_id', 'question_text']