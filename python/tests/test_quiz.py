import pytest
from quiz import Quiz
import logging
# Sample CSV content for testing
TEST_CSV = 'test_quiz_data.csv'

# Prepare a sample CSV file for tests
@pytest.fixture(scope="module", autouse=True)
def create_test_csv():
    with open(TEST_CSV, 'w', encoding='utf-8') as f:
        f.write("question,answer\n")
        f.write("What is the capital of France?,Paris\n")
        f.write("What is 2 + 2?,4\n")
        f.write("What is the largest planet in our solar system?,Jupiter\n")
    yield
    import os
    os.remove(TEST_CSV)

def test_load_quiz_data():
    quiz = Quiz(TEST_CSV)
    quiz.load_quiz_data()
    assert len(quiz.quiz_data) == 3
    assert quiz.quiz_data[0]['question'] == "What is the capital of France?"
    assert quiz.quiz_data[0]['answer'] == "Paris"

def test_check_answer():
    quiz = Quiz(TEST_CSV)
    # Test case-insensitive matching
    assert quiz.check_answer("paris", "Paris") is True
    assert quiz.check_answer("  Paris  ", "Paris") is True
    assert quiz.check_answer("london", "Paris") is False

def test_run_quiz(monkeypatch):
    quiz = Quiz(TEST_CSV)
    quiz.load_quiz_data()

    # Simulate user inputs for the quiz questions
    inputs = iter(["Paris", "3", "Jupiter"])

    # Patch input() to return values from inputs iterator
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    # Patch print to capture outputs (optional)
    outputs = []
    monkeypatch.setattr('builtins.print', lambda x: outputs.append(x))

    quiz.run_quiz()

    # Score should be 2 because the second answer is wrong
    assert quiz.score == 2

def test_show_score(capsys):
    quiz = Quiz(TEST_CSV)
    quiz.score = 2
    quiz.quiz_data = [{'question': 'Q1', 'answer': 'A1'}, {'question': 'Q2', 'answer': 'A2'}, {'question': 'Q3', 'answer': 'A3'}]

    quiz.show_score()
    captured = capsys.readouterr()
    assert "Your final score is 2 out of 3." in captured.out

def test_logging_output(caplog):
    caplog.set_level(logging.INFO)
    quiz = Quiz(TEST_CSV)
    quiz.run_quiz()
    assert "Quiz started." in caplog.text

def test_answer_case_and_whitespace(monkeypatch):
    quiz_data = [
        {'question': 'Q1', 'answer': 'Answer'},
        {'question': 'Q2', 'answer': 'Test'}
    ]
    quiz = Quiz('dummy.csv')
    quiz.quiz_data = quiz_data
    inputs = iter(['  answer  ', 'TEST'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    outputs = []
    monkeypatch.setattr('builtins.print', lambda x: outputs.append(x))
    quiz.run_quiz()
    assert quiz.score == 2
