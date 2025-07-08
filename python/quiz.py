"""
Quiz Logic
"""


import csv

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
            # self.quiz_data = [row for row in reader]
            self.quiz_data = list(reader)


    def present_question(self, question):
        """
        Presents a question to the user and accepts their answer.
        """
        print(question)
        answer = input("Your answer: ")
        return answer

    def check_answer(self, user_answer, correct_answer):
        """
        Checks if the user's answer is correct.
        """
        return user_answer.strip().lower() == correct_answer.strip().lower()

    def run_quiz(self):
        """
        Runs the quiz: presents each question, checks the answer, and updates the score.
        """
        self.score = 0
        for item in self.quiz_data:
            user_answer = self.present_question(item['question'])
            if self.check_answer(user_answer, item['answer']):
                print("Correct!\n")
                self.score += 1
            else:
                print("Wrong!\n")

    def show_score(self):
        """
        Displays the user's total score at the end of the quiz.
        """
        print(f"Your final score is {self.score} out of {len(self.quiz_data)}.")

if __name__ == "__main__":
    quiz = Quiz('quiz_data.csv')
    quiz.load_quiz_data()
    quiz.run_quiz()
    quiz.show_score()
