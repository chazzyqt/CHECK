class TestGrader:
    def __init__(self, answer_key, test_papers):
        self.answer_key = answer_key
        self.test_papers = test_papers
        self.key_answers = self._extract_answer_key()

    def _extract_answer_key(self):
        # Extract the answer key from the answer_key
        return [
            {qa["question_number"]: qa["answer"] for qa in test["question_answer_pairs"]}
            for test in self.answer_key["Question_pair"]["tests"]
        ]

    def grade_papers(self):
        # Iterate through the test papers and update scores
        for paper in self.test_papers:
            total_score = 0  # Initialize total score for this paper

            for test_index, test in enumerate(paper["Question_pair"]["tests"]):
                score = 0
                total_questions = len(test["question_answer_pairs"])

                # Compare answers with the answer key
                for qa in test["question_answer_pairs"]:
                    question_number = qa["question_number"]
                    user_answer = qa["answer"]
                    correct_answer = self.key_answers[test_index].get(question_number)

                    if user_answer == correct_answer:
                        score += 1
                        qa["is_correct"] = True  # Mark as correct
                    else:
                        qa["is_correct"] = False  # Mark as incorrect
                        qa["correct_answer"] = correct_answer  # Add the correct answer for reference

                # Calculate points for the test
                correct_points = (score / total_questions) * test["total_points"]
                test["correct_points"] = correct_points

                # Add to total score
                total_score += correct_points

            # Update the total score in student_info
            paper["Question_pair"]["student_info"]["total_score"] = total_score

    def get_updated_papers(self):
        # Return the updated test papers
        return self.test_papers
