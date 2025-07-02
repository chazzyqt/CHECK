import re
import json

class ExamDataProcessor:
    def __init__(self, combined_sections):
        # Expecting combined_sections to be a list of strings or list of objects containing strings
        self.combined_sections = combined_sections if isinstance(combined_sections, list) else [combined_sections]
        self.processed_sections = []

    def process(self):
        for section in self.combined_sections:
            student_info = {}
            tests = []
            image_name = section.get('original_url')
            get_full_data = section.get('full_data')
            # Ensure we are working with a string
            if isinstance(section, dict):
                section_text = section.get('full_section', '')  # Assuming the key for the string is 'content'
            else:
                section_text = section
            annotations = self.extract_annotations(section_text)
            matched_annots = self.match_annotations(get_full_data, annotations)
            cleaned_content = re.sub(r'\s+', ' ', section_text).strip()

            # Extract the name section and answer section
            name_section_match = re.search(r'^(.*?)(?=TEST\s+1)', cleaned_content, re.DOTALL)
            name_section = name_section_match.group(1).strip() if name_section_match else ""
            answer_section = cleaned_content[len(name_section):].strip()
            #print(name_section)
            #print(answer_section)
            student_info = self.extract_student_info(name_section)
            tests = self.parse_tests(answer_section)
            tests_with_annots  = self.process_annotations(tests, matched_annots)
            # Append each processed section as a dictionary to the list
            self.processed_sections.append({
                "image_name": image_name,
                "student_info": student_info,
                "tests": tests_with_annots
            })

    def sort_by_annotation(self,section):
        """Sorts a section by the 'annotation' value (removing the '.' and converting it to float)."""
        return sorted(section, key=lambda x: float(x['annotation'].replace('.', '')))

    def process_annotations(self,tests, result):
        """Processes the tests and their corresponding annotations, sorting by annotation."""
        currentNumber = 1
        annot = []
        
        # Iterate over the tests and sort the corresponding sections
        for item in tests:
            number_of_questions = len(item['question_answer_pairs'])
            if currentNumber == 1:
                #print(currentNumber, "before")
                section = self.sort_by_annotation(result[currentNumber: currentNumber + number_of_questions])
                currentNumber += number_of_questions
                annot.append(section)
                #print(currentNumber, "this is the current number")
            else:
               # print(currentNumber, "before")
                section = self.sort_by_annotation(result[currentNumber + 1: currentNumber + 1 + number_of_questions])
                currentNumber += 1 + number_of_questions
                annot.append(section)
                #print(currentNumber, "this is the current number")
        
        # Assign 'annotation' from annot to the question-answer pairs
        currentCount = 0
        for test, annotation in zip(tests, annot):
            currentCount += 1
            #print(f"Annotation {currentCount}: {annotation}")
            for pair, boxes in zip(test["question_answer_pairs"], annotation):
                pair['annotation'] = boxes["box"]
        
        return tests
    
    def match_annotations(self,full_data, final_annot):
        """
        Matches annotations with corresponding items in the data.

        Args:
            full_data (list): List of dictionaries, each containing 'box' and 'text' fields.
            final_annot (list): List of annotation strings to match.

        Returns:
            list: A list of matched annotations with their details.
        """
        matched_annotations = []
        current_element = 0

        # Loop through the full_data to match with annotations
        for item in full_data:
            # Check if the current annotation matches the text in the items
            if current_element < len(final_annot) and final_annot[current_element] in item['text']:
                matched_annotations.append({
                    'number': current_element + 1,  # Add 1 to make it human-readable
                    'annotation': final_annot[current_element],
                    'box': item['box'],
                    #'text': item['text']
                })
                # Move to the next annotation after finding the current one
                current_element += 1

                # If we have processed all annotations, break the loop
                if current_element >= len(final_annot):
                    break

        return matched_annotations

    def extract_annotations(self,text):
        """
        Extracts annotations (numbers followed by a period) from sections starting with 'TEST'.

        Args:
            text (str): The input text containing TEST sections and annotations.

        Returns:
            list: A list of annotations found in the text (e.g., ['1.', '6.', ...]).
        """
        # Split the text into the sections after each "TEST" occurrence
        sections = re.split(r'(?=TEST)', text)

        # Initialize a list to hold the annotations
        annotations = []

        # Iterate over the sections, skipping the ones before the first "TEST"
        for section in sections[1:]:  # Ignore the part before the first "TEST"
            # Find numbers followed by a period in the current section
            nums = re.findall(r'\b\d+\.', section)
            
            # Add the numbers to the annotations list
            annotations.extend(nums)

        return annotations

    def extract_student_info(self, name_section):
        return {
            "university": "De La Salle University - Dasmarinas",
            "college": "College of Science and Computer Studies",
            "department": "Computer Science Department",
            "exam_type": "Summative Examination",
            "subject_code": re.search(r'in (.*?) -', name_section).group(1) if re.search(r'in (.*?) -', name_section) else "",
            "subject_name": re.search(r'- (.*?) NAME:', name_section).group(1) if re.search(r'- (.*?) NAME:', name_section) else "",
            "name": re.search(r'NAME:\s*(.*?)\s*SCORE:', name_section).group(1) if re.search(r'NAME:\s*(.*?)\s*SCORE:', name_section) else "",
            "date": re.search(r'DATE:\s*(.*?)\s*PROGRAM', name_section).group(1) if re.search(r'DATE:\s*(.*?)\s*PROGRAM', name_section) else "",
            "program_code": re.search(r'PROGRAM CODE:\s*(\w+)', name_section).group(1) if re.search(r'PROGRAM CODE:\s*(\w+)', name_section) else "",
            "total_score": None
        }

    def parse_tests(self, answer_section):
        tests = []
        test_pattern = r'(TEST\s+(\d+)\.\s*(.*?)\s*\((\d+)\s*pts\.\))(.*?)(?=(TEST\s+\d+|$))'

        for match in re.finditer(test_pattern, answer_section, re.DOTALL):
            test_title = match.group(1)
            test_number = int(match.group(2))
            test_type = match.group(3).strip()
            points = int(match.group(4))
            test_body = match.group(5).strip()

            test_body_cleaned = re.sub(r'\s+', ' ', test_body).strip()
            question_answer_pairs = self.extract_questions_and_answers(test_body_cleaned)

            tests.append({
                "test_number": test_number,
                "test_type": test_type,
                "total_points": points,
                "correct_points": None,
                "full_text": test_body_cleaned,
                "question_answer_pairs": question_answer_pairs
            })
        
        return tests
    def extract_questions_and_answers(self, content):
    # Improved regular expression to better capture question-answer pairs
        pattern = r'(\d+)\.\s*([A-Za-z0-9\s\-.,]+?)(?=\s*\d+\.|$)'
        
        # Find all matches of question-answer pairs
        questions = re.findall(pattern, content)

        # Remove pairs where question_number == 0
        questions_and_answers = [{"question_number": int(q.strip()), "answer": a.strip('.').strip().replace(' ', '').upper()} for q, a in questions]
        questions_and_answers = [qa for qa in questions_and_answers if qa["question_number"] > 0]
        
        # Track the number of questions removed (those with question_number == 0)
        removed_count = len(questions) - len(questions_and_answers)

        # Create a sorted list of questions and answers
        questions_and_answers = sorted(questions_and_answers, key=lambda x: x["question_number"])

        # Get the last question number (the highest one in the sorted list)
        last_question_number = questions_and_answers[-1]["question_number"] if questions_and_answers else 0

        # Ensure that all question numbers from 1 to the last number are present
        all_question_numbers = set(range(1, last_question_number + 1))
        current_question_numbers = {item["question_number"] for item in questions_and_answers}

        # Find the missing question numbers
        missing_question_numbers = all_question_numbers - current_question_numbers

        # Add missing questions with a default answer (or handle as needed)
        for missing_number in missing_question_numbers:
            questions_and_answers.append({"question_number": missing_number, "answer": "N/A"})  # Default answer for missing questions

        # Sort the list again after adding missing questions
        questions_and_answers = sorted(questions_and_answers, key=lambda x: x["question_number"])

        # Re-add the "N/A" answers at the end after removing invalid ones, using the last valid question number
        for i in range(removed_count):
            last_question_number += 1
            questions_and_answers.append({"question_number": last_question_number, "answer": "N/A"})

        # Sort the list again after re-adding removed questions (in case any were appended out of order)
        questions_and_answers = sorted(questions_and_answers, key=lambda x: x["question_number"])

        return questions_and_answers
    # def extract_questions_and_answers(self, content):
    # # Improved regular expression to better capture question-answer pairs
    # # This assumes that the question number is followed by a period, then answer(s) that are separated by spaces
    #     pattern = r'(\d+)\.\s*([A-Za-z0-9\s\-.,]+?)(?=\s*\d+\.|$)'
        
    #     questions = re.findall(pattern, content)
        
    #     # Create a sorted list of questions and answers
    #     questions_and_answers = sorted(
    #         [{"question_number": int(q.strip()), "answer": a.strip('.').strip().replace(' ', '').upper()} for q, a in questions],
    #         key=lambda x: x["question_number"]
    #     )
        
    #     # Get the last question number (the highest one in the sorted list)
    #     last_question_number = questions_and_answers[-1]["question_number"] if questions_and_answers else 0
        
    #     # Ensure that all question numbers from 1 to the last number are present
    #     all_question_numbers = set(range(1, last_question_number + 1))
    #     current_question_numbers = {item["question_number"] for item in questions_and_answers}
        
    #     # Find the missing question numbers
    #     missing_question_numbers = all_question_numbers - current_question_numbers
        
    #     # Add missing questions with a default answer (or handle as needed)
    #     for missing_number in missing_question_numbers:
    #         questions_and_answers.append({"question_number": missing_number, "answer": "N/A"})  # Default answer for missing questions
        
    #     # Sort the list again after adding missing questions
    #     questions_and_answers = sorted(questions_and_answers, key=lambda x: x["question_number"])
        
    #     return questions_and_answers

    def validate_json_data(self):
        issues = []
        valid_answers_MC = {"A", "B", "C", "D", "E", "F"}

        for section in self.processed_sections:
            student_info = section["student_info"]
            tests = section["tests"]

            # Check student info
            if not student_info['name']:
                issues.append("Missing student name.")

            for test in tests:
                if not test['test_type']:
                    issues.append(f"Test {test['test_number']} is missing a type.")
                if test['total_points'] <= 0:
                    issues.append(f"Test {test['test_number']} has invalid points.")
                if not test['question_answer_pairs']:
                    issues.append(f"Test {test['test_number']} has no question-answer pairs.")

                for qa in test['question_answer_pairs']:
                    if qa['question_number'] <= 0:
                        issues.append(f"Test {test['test_number']}, question {qa['question_number']} has an invalid number.")
                    if not qa['answer']:
                        issues.append(f"Test {test['test_number']}, question {qa['question_number']} has no answer.")

                    answer = qa['answer']
                    if test['test_type'].lower() == "multiple choice":
                        if answer not in valid_answers_MC:
                            issues.append(f"Test {test['test_number']}, question {qa['question_number']} has an invalid answer: {answer}.")
                    elif test['test_type'].lower() == "true or false":
                        if answer not in ["T", "F", "TRUE", "FALSE"]:
                            issues.append(f"Test {test['test_number']}, question {qa['question_number']} has an invalid true/false answer: {answer}.")
                    elif test['test_type'].lower() == "matching type":
                        if not re.match(r'^[A-Z]$', answer):
                            issues.append(f"Test {test['test_number']}, question {qa['question_number']} has an invalid matching answer: {answer}.")

        return issues

    def get_output_json(self):
        return self.processed_sections


# Example usage:
# combined_sections = [{'original_url': 'http://res.cloudinary.com/djdjamrmj/image/upload/v1731711488/CHECK/not_folder_short1.jpg', 'original_size': (1452, 2048), 'full_data': [{'box': (532, 176, 568, 202), 'text': 'De'}, {'box': (568, 176, 600, 202), 'text': 'La'}, {'box': (602, 176, 662, 204), 'text': 'Salle'}, {'box': (662, 176, 778, 206), 'text': 'University'}, {'box': (774, 182, 800, 204), 'text': '-'}, {'box': (798, 176, 934, 202), 'text': 'Dasmarinas'}, {'box': (442, 200, 560, 228), 'text': 'COLLEGE'}, {'box': (558, 200, 600, 230), 'text': 'OF'}, {'box': (598, 202, 706, 228), 'text': 'SCIENCE'}, {'box': (702, 200, 762, 230), 'text': 'AND'}, {'box': (759, 202, 898, 228), 'text': 'COMPUTER'}, {'box': (896, 200, 1002, 228), 'text': 'STUDIES'}, {'box': (518, 228, 654, 256), 'text': 'COMPUTER'}, {'box': (654, 230, 762, 256), 'text': 'SCIENCE'}, {'box': (762, 228, 926, 254), 'text': 'DEPARTMENT'}, {'box': (448, 254, 568, 282), 'text': 'Summerive'}, {'box': (568, 256, 698, 282), 'text': 'Examination'}, {'box': (696, 256, 722, 282), 'text': 'in'}, {'box': (722, 256, 854, 284), 'text': 'subjectCode'}, {'box': (852, 262, 872, 278), 'text': '-'}, {'box': (868, 256, 1005, 284), 'text': 'subjectName'}, {'box': (290, 302, 379, 332), 'text': 'NAME:'}, {'box': (384, 292, 516, 336), 'text': 'JESHVEL'}, {'box': (514, 296, 612, 334), 'text': 'JERSEY'}, {'box': (612, 294, 714, 334), 'text': 'M.SOSA'}, {'box': (749, 302, 860, 332), 'text': 'SCORE:'}, {'box': (291, 352, 379, 388), 'text': 'DATE:'}, {'box': (417, 346, 544, 384), 'text': 'OCTOBER'}, {'box': (550, 346, 594, 384), 'text': '21'}, {'box': (604, 344, 682, 382), 'text': '2024'}, {'box': (752, 356, 896, 384), 'text': 'PROGRAM'}, {'box': (900, 354, 990, 384), 'text': 'CODE:'}, {'box': (1012, 348, 1114, 388), 'text': 'BCS42'}, {'box': (294, 460, 369, 490), 'text': 'TEST'}, {'box': (378, 460, 406, 490), 'text': '1.'}, {'box': (410, 462, 516, 492), 'text': 'Multiple'}, {'box': (520, 462, 616, 492), 'text': 'Choice'}, {'box': (618, 462, 664, 496), 'text': '(30'}, {'box': (666, 464, 727, 496), 'text': 'pts.)'}, {'box': (363, 514, 392, 544), 'text': '1.'}, {'box': (404, 510, 454, 546), 'text': 'A'}, {'box': (562, 508, 644, 550), 'text': '6.b'}, {'box': (754, 
# 514, 800, 548), 'text': '11.'}, {'box': (806, 510, 850, 548), 'text': '9'}, {'box': (360, 560, 394, 596), 'text': '2.'}, {'box': (410, 556, 452, 592), 'text': 'B'}, {'box': (562, 562, 646, 598), 'text': '7.C'}, {'box': (754, 564, 802, 596), 'text': '12.'}, {'box': (800, 554, 852, 598), 'text': 'd'}, {'box': (363, 612, 392, 644), 'text': '3.'}, {'box': (414, 610, 449, 636), 'text': 'c'}, {'box': (560, 602, 648, 650), 'text': '8.2'}, {'box': (754, 612, 802, 646), 'text': 
# '13.'}, {'box': (798, 608, 844, 646), 'text': 'b'}, {'box': (360, 662, 408, 694), 'text': '4.'}, {'box': (398, 662, 454, 696), 'text': 'I'}, {'box': (560, 660, 648, 698), 'text': '9.C'}, {'box': (752, 662, 798, 696), 'text': '14.'}, {'box': (810, 660, 842, 686), 'text': 'c'}, {'box': (362, 712, 394, 744), 'text': '5.'}, {'box': (401, 704, 454, 746), 'text': 'A'}, {'box': (548, 712, 594, 744), 'text': '10.'}, {'box': (594, 712, 644, 746), 'text': 'a'}, {'box': (752, 712, 798, 746), 'text': '15.'}, {'box': (806, 710, 850, 746), 'text': '9'}, {'box': (288, 812, 366, 842), 'text': 'TEST'}, {'box': (374, 812, 401, 842), 'text': '2.'}, {'box': (404, 812, 468, 842), 'text': 'true'}, {'box': (470, 818, 504, 842), 'text': 'or'}, {'box': (506, 814, 580, 844), 'text': 'False'}, {'box': (582, 814, 628, 848), 'text': '(10'}, {'box': (630, 814, 690, 848), 'text': 'pts.)'}, {'box': (362, 866, 388, 894), 'text': '1.'}, {'box': (494, 860, 576, 900), 'text': 'true'}, {'box': (818, 866, 850, 898), 'text': '6.'}, {'box': (944, 852, 970, 884), 'text': 'F'}, {'box': (360, 914, 388, 942), 'text': '2.'}, {'box': 
# (504, 906, 584, 946), 'text': 'False'}, {'box': (818, 916, 845, 946), 'text': '7.'}, {'box': (946, 924, 962, 940), 'text': 'U'}, {'box': (954, 942, 978, 984), 'text': 'f'}, {'box': (360, 964, 388, 994), 'text': '3.'}, {'box': (494, 960, 586, 998), 'text': 'TRUE'}, {'box': (818, 964, 845, 994), 'text': '8.'}, {'box': (948, 996, 973, 1024), 'text': 'f'}, {'box': (360, 1012, 388, 1040), 'text': '4.'}, {'box': (504, 1002, 590, 1044), 'text': 'FALSE'}, {'box': (816, 1014, 844, 1042), 'text': '9.'}, {'box': (360, 1062, 388, 1092), 'text': '5.'}, {'box': (504, 1054, 538, 1094), 'text': 'T'}, {'box': (800, 1062, 845, 1094), 'text': 
# '10.'}, {'box': (944, 1048, 980, 1086), 'text': 't'}, {'box': (286, 1162, 363, 1190), 'text': 'TEST'}, {'box': (372, 1162, 404, 1194), 'text': '3.'}, {'box': 
# (414, 1164, 534, 1194), 'text': 'Matching'}, {'box': (538, 1164, 604, 1196), 'text': 'Type'}, {'box': (606, 1162, 652, 1196), 'text': '(10'}, {'box': (654, 1162, 714, 1196), 'text': 'pts.)'}, {'box': (360, 1212, 388, 1242), 'text': '1.'}, {'box': (400, 1204, 449, 1248), 'text': 'A'}, {'box': (556, 1208, 640, 1248), 'text': '6.C'}, {'box': (358, 1262, 390, 1294), 'text': '2.'}, {'box': (406, 1252, 448, 1292), 'text': 'E'}, {'box': (554, 1246, 640, 1298), 'text': '7.B'}, 
# {'box': (358, 1310, 390, 1342), 'text': '3.'}, {'box': (400, 1306, 449, 1342), 'text': 'F'}, {'box': (556, 1302, 640, 1342), 'text': '8.U'}, {'box': (358, 1358, 385, 1388), 'text': '4.'}, {'box': (408, 1344, 444, 1386), 'text': 'H'}, {'box': (552, 1346, 638, 1394), 'text': '9.G'}, {'box': (355, 1406, 388, 1438), 'text': '5.'}, {'box': (400, 1398, 446, 1436), 'text': 'D'}, {'box': (542, 1404, 588, 1438), 'text': '10.'}, {'box': (596, 1392, 632, 1432), 'text': 'I'}], 'full_section': 'De La Salle University - Dasmarinas COLLEGE OF SCIENCE AND COMPUTER STUDIES COMPUTER SCIENCE DEPARTMENT Summerive Examination in subjectCode - subjectName NAME: JESHVEL JERSEY M.SOSA SCORE: DATE: OCTOBER 21 2024 PROGRAM CODE: BCS42 TEST 1. Multiple Choice (30 pts.) 1. A 6.b 11. 9 2. B 7.C 12. d 3. c 8.2 13. b 4. I 9.C 14. c 5. A 10. a 15. 9 TEST 2. true or False (10 pts.) 1. true 6. F 2. False 7. U f 3. TRUE 8. f 4. FALSE 9. 5. T 10. t TEST 3. Matching Type (10 pts.) 1. A 6.C 2. E 7.B 3. F 8.U 4. H 9.G 5. D 10. I'}, {'original_url': 'http://res.cloudinary.com/djdjamrmj/image/upload/v1731711488/CHECK/not_folder_short1.jpg', 'original_size': (1452, 2048), 'full_data': [{'box': (532, 176, 568, 202), 'text': 'De'}, {'box': (568, 176, 600, 202), 'text': 'La'}, {'box': (602, 176, 662, 204), 'text': 'Salle'}, {'box': (662, 176, 778, 206), 'text': 'University'}, {'box': (774, 182, 800, 204), 'text': '-'}, {'box': (798, 176, 934, 202), 'text': 'Dasmarinas'}, {'box': (442, 200, 560, 228), 'text': 'COLLEGE'}, {'box': (558, 200, 600, 230), 'text': 'OF'}, {'box': (598, 202, 706, 228), 'text': 'SCIENCE'}, {'box': (702, 200, 762, 230), 'text': 'AND'}, {'box': (759, 202, 898, 228), 'text': 'COMPUTER'}, {'box': (896, 200, 1002, 228), 'text': 'STUDIES'}, {'box': (518, 228, 654, 256), 'text': 'COMPUTER'}, {'box': (654, 230, 762, 256), 'text': 'SCIENCE'}, {'box': (762, 228, 926, 254), 'text': 'DEPARTMENT'}, {'box': (448, 254, 568, 282), 'text': 'Summerive'}, {'box': (568, 256, 698, 282), 'text': 'Examination'}, {'box': (696, 256, 722, 282), 'text': 'in'}, {'box': (722, 256, 854, 284), 'text': 'subjectCode'}, {'box': (852, 262, 872, 278), 'text': '-'}, {'box': (868, 256, 1005, 284), 'text': 'subjectName'}, {'box': (290, 302, 379, 332), 'text': 'NAME:'}, {'box': (384, 292, 516, 336), 'text': 'JESHVEL'}, {'box': (514, 296, 612, 334), 'text': 'JERSEY'}, {'box': (612, 294, 714, 334), 'text': 'M.SOSA'}, {'box': (749, 302, 860, 332), 'text': 'SCORE:'}, {'box': (291, 352, 379, 388), 'text': 'DATE:'}, {'box': (417, 346, 544, 384), 'text': 'OCTOBER'}, {'box': (550, 346, 594, 384), 'text': '21'}, {'box': (604, 344, 682, 382), 'text': '2024'}, {'box': (752, 356, 896, 384), 'text': 'PROGRAM'}, {'box': (900, 354, 990, 384), 'text': 'CODE:'}, {'box': (1012, 348, 1114, 388), 'text': 'BCS42'}, {'box': (294, 460, 369, 490), 'text': 'TEST'}, {'box': (378, 460, 406, 490), 'text': '1.'}, {'box': (410, 462, 516, 492), 'text': 'Multiple'}, {'box': (520, 462, 616, 492), 'text': 'Choice'}, {'box': (618, 462, 664, 496), 'text': '(30'}, {'box': (666, 464, 727, 496), 'text': 'pts.)'}, {'box': (363, 514, 392, 544), 'text': '1.'}, {'box': (404, 510, 454, 546), 'text': 'A'}, {'box': (562, 508, 644, 550), 'text': '6.b'}, {'box': (754, 
# 514, 800, 548), 'text': '11.'}, {'box': (806, 510, 850, 548), 'text': '9'}, {'box': (360, 560, 394, 596), 'text': '2.'}, {'box': (410, 556, 452, 592), 'text': 'B'}, {'box': (562, 562, 646, 598), 'text': '7.C'}, {'box': (754, 564, 802, 596), 'text': '12.'}, {'box': (800, 554, 852, 598), 'text': 'd'}, {'box': (363, 612, 392, 644), 'text': '3.'}, {'box': (414, 610, 449, 636), 'text': 'c'}, {'box': (560, 602, 648, 650), 'text': '8.2'}, {'box': (754, 612, 802, 646), 'text': 
# '13.'}, {'box': (798, 608, 844, 646), 'text': 'b'}, {'box': (360, 662, 408, 694), 'text': '4.'}, {'box': (398, 662, 454, 696), 'text': 'I'}, {'box': (560, 660, 648, 698), 'text': '9.C'}, {'box': (752, 662, 798, 696), 'text': '14.'}, {'box': (810, 660, 842, 686), 'text': 'c'}, {'box': (362, 712, 394, 744), 'text': '5.'}, {'box': (401, 704, 454, 746), 'text': 'A'}, {'box': (548, 712, 594, 744), 'text': '10.'}, {'box': (594, 712, 644, 746), 'text': 'a'}, {'box': (752, 712, 798, 746), 'text': '15.'}, {'box': (806, 710, 850, 746), 'text': '9'}, {'box': (288, 812, 366, 842), 'text': 'TEST'}, {'box': (374, 812, 401, 842), 'text': '2.'}, {'box': (404, 812, 468, 842), 'text': 'true'}, {'box': (470, 818, 504, 842), 'text': 'or'}, {'box': (506, 814, 580, 844), 'text': 'False'}, {'box': (582, 814, 628, 848), 'text': '(10'}, {'box': (630, 814, 690, 848), 'text': 'pts.)'}, {'box': (362, 866, 388, 894), 'text': '1.'}, {'box': (494, 860, 576, 900), 'text': 'true'}, {'box': (818, 866, 850, 898), 'text': '6.'}, {'box': (944, 852, 970, 884), 'text': 'F'}, {'box': (360, 914, 388, 942), 'text': '2.'}, {'box': 
# (504, 906, 584, 946), 'text': 'False'}, {'box': (818, 916, 845, 946), 'text': '7.'}, {'box': (946, 924, 962, 940), 'text': 'U'}, {'box': (954, 942, 978, 984), 'text': 'f'}, {'box': (360, 964, 388, 994), 'text': '3.'}, {'box': (494, 960, 586, 998), 'text': 'TRUE'}, {'box': (818, 964, 845, 994), 'text': '8.'}, {'box': (948, 996, 973, 1024), 'text': 'f'}, {'box': (360, 1012, 388, 1040), 'text': '4.'}, {'box': (504, 1002, 590, 1044), 'text': 'FALSE'}, {'box': (816, 1014, 844, 1042), 'text': '9.'}, {'box': (360, 1062, 388, 1092), 'text': '5.'}, {'box': (504, 1054, 538, 1094), 'text': 'T'}, {'box': (800, 1062, 845, 1094), 'text': 
# '10.'}, {'box': (944, 1048, 980, 1086), 'text': 't'}, {'box': (286, 1162, 363, 1190), 'text': 'TEST'}, {'box': (372, 1162, 404, 1194), 'text': '3.'}, {'box': 
# (414, 1164, 534, 1194), 'text': 'Matching'}, {'box': (538, 1164, 604, 1196), 'text': 'Type'}, {'box': (606, 1162, 652, 1196), 'text': '(10'}, {'box': (654, 1162, 714, 1196), 'text': 'pts.)'}, {'box': (360, 1212, 388, 1242), 'text': '1.'}, {'box': (400, 1204, 449, 1248), 'text': 'A'}, {'box': (556, 1208, 640, 1248), 'text': '6.C'}, {'box': (358, 1262, 390, 1294), 'text': '2.'}, {'box': (406, 1252, 448, 1292), 'text': 'E'}, {'box': (554, 1246, 640, 1298), 'text': '7.B'}, 
# {'box': (358, 1310, 390, 1342), 'text': '3.'}, {'box': (400, 1306, 449, 1342), 'text': 'F'}, {'box': (556, 1302, 640, 1342), 'text': '8.U'}, {'box': (358, 1358, 385, 1388), 'text': '4.'}, {'box': (408, 1344, 444, 1386), 'text': 'H'}, {'box': (552, 1346, 638, 1394), 'text': '9.G'}, {'box': (355, 1406, 388, 1438), 'text': '5.'}, {'box': (400, 1398, 446, 1436), 'text': 'D'}, {'box': (542, 1404, 588, 1438), 'text': '10.'}, {'box': (596, 1392, 632, 1432), 'text': 'I'}], 'full_section': 'De La Salle University - Dasmarinas COLLEGE OF SCIENCE AND COMPUTER STUDIES COMPUTER SCIENCE DEPARTMENT Summerive Examination in subjectCode - subjectName NAME: JESHVEL JERSEY M.SOSA SCORE: DATE: OCTOBER 21 2024 PROGRAM CODE: BCS42 TEST 1. Multiple Choice (30 pts.) 1. A 6.b 11. 9 2. B 7.C 12. d 3. c 8.2 13. b 4. I 9.C 14. c 5. A 10. a 15. 9 TEST 2. true or False (10 pts.) 1. true 6. F 2. False 7. U f 3. TRUE 8. f 4. FALSE 9. 5. T 10. t TEST 3. Matching Type (10 pts.) 1. A 6.C 2. E 7.B 3. F 8.U 4. H 9.G 5. D 10. I'}]

# processor = ExamDataProcessor(combined_sections)
# processor.process()
# output_json = processor.get_output_json()
# validation_issues = processor.validate_json_data()

# # Output JSON data and validation issues
# print(json.dumps(output_json, indent=4))
# if validation_issues:
#     print("\nValidation Issues:")
#     for issue in validation_issues:
#         print(f"- {issue}")
