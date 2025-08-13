import django_filters
from .models import Score


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
