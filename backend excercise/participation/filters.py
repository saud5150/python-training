import django_filters
from django_filters import rest_framework as filters
from .score.models import Score
from .answer.models import Answer
from .quiz.models import Quiz as ParticipationQuiz
from .task.models import Task


class ScoreFilter(django_filters.FilterSet):
    """
    Filter for Score model with aggregate score thresholds
    
    Common usage examples:
    - ?min_aggregate_score=70 (scores 70 and above)
    - ?min_aggregate_score=50&max_aggregate_score=80 (scores between 50-80)
    - ?subject_id=uuid&min_aggregate_score=60 (subject scores above 60)
    """
    
    # Filter for minimum aggregate score (gte = greater than or equal)
    min_aggregate_score = django_filters.NumberFilter(
        field_name='aggregate_score', 
        lookup_expr='gte',
        help_text='Minimum aggregate score. Examples: 50 (above average), 70 (good), 80 (excellent)'
    )
    
    # Filter for maximum aggregate score (lte = less than or equal)
    max_aggregate_score = django_filters.NumberFilter(
        field_name='aggregate_score', 
        lookup_expr='lte',
        help_text='Maximum aggregate score. Use with min_aggregate_score to create ranges'
    )
    
    # Filter by subject
    subject_id = django_filters.UUIDFilter(
        field_name='subject_id',
        help_text='Filter by subject UUID - get scores for specific subject only'
    )
    
    # Filter by user
    user_id = django_filters.UUIDFilter(
        field_name='user_id',
        help_text='Filter by user UUID - get scores for specific user only'
    )
    
    # Date range filters
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Created after this date. Format: 2023-01-01T00:00:00Z'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Created before this date. Format: 2023-12-31T23:59:59Z'
    )
    
    class Meta:
        model = Score
        fields = {
            'aggregate_score': ['exact', 'gte', 'lte', 'gt', 'lt'],
        }


class AnswerFilter(django_filters.FilterSet):
    """
    Filter for Answer model with comprehensive filtering options
    
    Common usage examples:
    - ?user_quiz_id=uuid (answers for specific user-quiz combination)
    - ?question_id=uuid (answers for specific question)
    - ?is_correct=true (only correct answers)
    - ?user_id=uuid (all answers by specific user)
    - ?quiz_id=uuid (all answers for specific quiz)
    """
    
    # Filter by user-quiz relationship
    user_quiz_id = django_filters.UUIDFilter(
        field_name='user_quiz_id__id',
        help_text='Filter by user-quiz ID - get answers for specific user-quiz combination'
    )
    
    # Filter by question
    question_id = django_filters.UUIDFilter(
        field_name='question_id__id',
        help_text='Filter by question ID - get answers for specific question'
    )
    
    # Filter by user (through user-quiz relationship)
    user_id = django_filters.UUIDFilter(
        field_name='user_quiz_id__user_id__id',
        help_text='Filter by user ID - get all answers by specific user'
    )
    
    # Filter by quiz (through user-quiz relationship)
    quiz_id = django_filters.UUIDFilter(
        field_name='user_quiz_id__quiz_id__id',
        help_text='Filter by quiz ID - get all answers for specific quiz'
    )
    
    # Filter by subject (through quiz relationship)
    subject_id = django_filters.UUIDFilter(
        field_name='user_quiz_id__quiz_id__subject_id__id',
        help_text='Filter by subject ID - get answers for quizzes in specific subject'
    )
    
    # Filter by correctness
    is_correct = django_filters.BooleanFilter(
        field_name='is_correct',
        help_text='Filter by answer correctness - true for correct, false for incorrect'
    )
    
    # Filter by answer text content
    answer_text = django_filters.CharFilter(
        field_name='answer_text',
        lookup_expr='icontains',
        help_text='Filter by answer text content (case-insensitive contains)'
    )
    
    # Date range filters
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Answers created after this date. Format: 2023-01-01T00:00:00Z'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Answers created before this date. Format: 2023-12-31T23:59:59Z'
    )
    
    class Meta:
        model = Answer
        fields = ['user_quiz_id', 'question_id', 'is_correct']


class QuizFilter(django_filters.FilterSet):
    """
    Filter for Quiz (participation) model with score and completion filtering
    
    Common usage examples:
    - ?user_id=uuid (quizzes taken by specific user)
    - ?quiz_id=uuid (specific quiz instances)
    - ?min_score=70 (quizzes with score 70 and above)
    - ?completed=true (only completed quizzes)
    - ?subject_id=uuid (quizzes for specific subject)
    """
    
    # Filter by user
    user_id = django_filters.UUIDFilter(
        field_name='user_id__id',
        help_text='Filter by user ID - get quizzes taken by specific user'
    )
    
    # Filter by assigned quiz
    quiz_id = django_filters.UUIDFilter(
        field_name='quiz_id__id',
        help_text='Filter by quiz ID - get instances of specific quiz'
    )
    
    # Filter by subject (through quiz relationship)
    subject_id = django_filters.UUIDFilter(
        field_name='quiz_id__subject_id__id',
        help_text='Filter by subject ID - get quizzes for specific subject'
    )
    
    # Score range filters
    min_score = django_filters.NumberFilter(
        field_name='score',
        lookup_expr='gte',
        help_text='Minimum score threshold. Examples: 50 (pass), 70 (good), 80 (excellent)'
    )
    
    max_score = django_filters.NumberFilter(
        field_name='score',
        lookup_expr='lte',
        help_text='Maximum score threshold. Use with min_score for score ranges'
    )
    
    # Exact score filter
    score = django_filters.NumberFilter(
        field_name='score',
        lookup_expr='exact',
        help_text='Exact score match'
    )
    
    # Question count filters
    min_total_questions = django_filters.NumberFilter(
        field_name='total_questions',
        lookup_expr='gte',
        help_text='Minimum number of questions in quiz'
    )
    
    min_total_correct = django_filters.NumberFilter(
        field_name='total_correct',
        lookup_expr='gte',
        help_text='Minimum number of correct answers'
    )
    
    # Completion status filter
    completed = django_filters.BooleanFilter(
        method='filter_completed',
        help_text='Filter by completion status - true for completed, false for incomplete'
    )
    
    def filter_completed(self, queryset, name, value):
        """Filter quizzes by completion status"""
        if value:
            return queryset.filter(completed_at__isnull=False)
        return queryset.filter(completed_at__isnull=True)
    
    # Date range filters
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Quiz attempts created after this date'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Quiz attempts created before this date'
    )
    
    completed_after = django_filters.DateTimeFilter(
        field_name='completed_at',
        lookup_expr='gte',
        help_text='Quizzes completed after this date'
    )
    
    completed_before = django_filters.DateTimeFilter(
        field_name='completed_at',
        lookup_expr='lte',
        help_text='Quizzes completed before this date'
    )
    
    class Meta:
        model = ParticipationQuiz
        fields = ['user_id', 'quiz_id', 'score', 'total_questions', 'total_correct']


class TaskFilter(filters.FilterSet):
    # Type filter
    type = filters.ChoiceFilter(
        choices=Task.TaskType.choices,  # Use the choices from your model
        help_text="Filter by task type (quiz, reminder, todo)"
    )

    # Text filters
    title = filters.CharFilter(
        lookup_expr='icontains',
        help_text="Filter by task title (contains)"
    )
    
    description = filters.CharFilter(
        lookup_expr='icontains',
        help_text="Filter by task description (contains)"
    )
    
    # Status filters
    status = filters.ChoiceFilter(
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        help_text="Filter by task status"
    )
    
    # Priority filters
    priority = filters.ChoiceFilter(
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        help_text="Filter by task priority"
    )
    
    # User filters
    assigned_to = filters.UUIDFilter(
        field_name='user_id',
        help_text="Filter by assigned user ID"
    )
    
    created_by = filters.UUIDFilter(
        field_name='created_by_id',
        help_text="Filter by creator user ID"
    )
    
    # Date filters
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter tasks created after this date"
    )
    
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter tasks created before this date"
    )
    
    due_after = filters.DateTimeFilter(
        field_name='due_date',
        lookup_expr='gte',
        help_text="Filter tasks due after this date"
    )
    
    due_before = filters.DateTimeFilter(
        field_name='due_date',
        lookup_expr='lte',
        help_text="Filter tasks due before this date"
    )
    
    # Boolean filters
    is_completed = filters.BooleanFilter(
        method='filter_is_completed',
        help_text="Filter by completion status"
    )
    
    is_overdue = filters.BooleanFilter(
        method='filter_is_overdue',
        help_text="Filter overdue tasks"
    )
    
    # Ordering
    ordering = filters.OrderingFilter(
        fields=(
            ('title', 'title'),
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
            ('due_date', 'due_date'),
            ('priority', 'priority'),
            ('status', 'status'),
        ),
        field_labels={
            'title': 'Title',
            'created_at': 'Created Date',
            'updated_at': 'Updated Date',
            'due_date': 'Due Date',
            'priority': 'Priority',
            'status': 'Status',
        }
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'priority',
            'assigned_to', 'created_by', 'created_after', 'created_before',
            'due_after', 'due_before', 'is_completed', 'is_overdue'
        ]
    