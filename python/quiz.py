"""
Quiz Logic
"""


import csv
import logging

logging.basicConfig(
    level=logging.INFO,
    filename='quiz.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Quiz:
    """
    Quiz class
    [arg] filename of quiz file
    """
    def __init__(self, filename):
        self.filename = filename
        self.quiz_data = []
        self.score = 0

    def load_quiz_data(self):
        """
        Reads questions and answers from a CSV file.
        Populates self.quiz_data with a list of dictionaries.
        """
        with open(self.filename, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.quiz_data = list(reader)


    def present_question(self, question):
        """
        Presents a question to the user and accepts their answer.
        """
        print(question)
        answer = input("Your answer: ")
        logging.info(f"User answered: '{answer}' for question: '{question}'")
        return answer

    def check_answer(self, user_answer, correct_answer):
        """
        Checks if the user's answer is correct
        """
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        logging.info(f"User answered: , '{user_answer}',  for correct answer: , '{is_correct}'")
        return is_correct

    def run_quiz(self):
        """
        Runs the quiz: presents each question, checks the answer, and updates the score.
        """
        logging.info("Quiz started.")
        self.score = 0
        for item in self.quiz_data:
            user_answer = self.present_question(item['question'])
            if self.check_answer(user_answer, item['answer']):
                logging.info("Correct!")
                self.score += 1
            else:
                logging.info("Wrong!")

        logging.info("Quiz completed.")

    def show_score(self):
        """
        Displays the user's total score at the end of the quiz.
        """
        logging.info(f"Quiz final score: {self.score} out of {len(self.quiz_data)}.")

if __name__ == "__main__":
    quiz = Quiz('quiz_data.csv')
    quiz.load_quiz_data()
    quiz.run_quiz()
    quiz.show_score()
