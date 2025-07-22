import csv
from io import TextIOWrapper
from rest_framework.response import Response
from rest_framework import status
from quiz.models import Subject, Quiz, Question
from datetime import datetime

def process_question_csv_upload(request):
    subject_id = request.data.get('id')
    if not subject_id:
        return Response({'error': 'subject_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response({'error': f'Subject with id {subject_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    quiz_title = f"Uploaded Quiz {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    quiz = Quiz.objects.create(title=quiz_title, description="Bulk uploaded via CSV", subject_id=subject)

    file_obj = request.FILES.get('file')
    if not file_obj:
        quiz.delete()
        return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
    decoded_file = TextIOWrapper(file_obj, encoding='utf-8')
    reader = csv.DictReader(decoded_file)
    # Normalize fieldnames to lowercase and strip whitespace
    normalized_fields = [f.strip().lower() for f in reader.fieldnames]
    if set(normalized_fields) != {'question', 'answer'}:
        quiz.delete()
        return Response({'error': 'CSV must have columns: question, answer (case-insensitive, no extra columns)'}, status=status.HTTP_400_BAD_REQUEST)
    # Map original fieldnames to normalized
    field_map = {f.strip().lower(): f for f in reader.fieldnames}
    questions = []
    errors = []
    for idx, row in enumerate(reader, start=2):  # start=2 for header row
        question_text = row.get(field_map['question'], '').strip()
        answer_text = row.get(field_map['answer'], '').strip()
        if not question_text or not answer_text:
            errors.append(f"Row {idx}: Both question and answer must be filled.")
        else:
            questions.append(Question(question_text=question_text, correct_answer=answer_text, quiz_id=quiz))
    if errors:
        quiz.delete()
        return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
    Question.objects.bulk_create(questions)
    return Response({'status': 'success', 'inserted': len(questions), 'quiz_id': str(quiz.id), 'quiz_title': quiz.title, 'subject_id': str(subject.id), 'subject_name': subject.name}) 