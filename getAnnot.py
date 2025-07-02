import re

def extract_annotations(text):
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

# Example usage
text = """
De La Salle University - Dasmaninas COLLEGE OF SCIENCE AND COMPUTER STUDIES COMPUTER SCIENCE DEPARTMENT Summerive Examination in subjectCode - subjectName NAME: JOHN DOE SCORE: DATE: NOVEMBER 212014 PROGRAM CODE: BCS42 TEST 1. Identication (20 pts.) 1. DATA 6. COMPUTER 2. SCIENCE 7. RAM 3. MACHINE LEARNING 8. DBMS 4. NEURAL NETWORK 9. LANGUAGE 5. THESIS 10. DATA BASE TEST 2. Matching Type (15 pts.) 1. A 6. F 11. K 2. B 
7. G 12. L 3. c 8.14 13. M 4. D 9. I 14. N 5. E 10. J 15. 0 TEST 3. Fill in the blanks (10 pts.) 1. ALGORITHM 6. PARALLELISM 2. COMPILER 7. QUERY 3. DATA STRUCTURE 8. HASHING 4. RECURSION 9. MODEL 5. APII 10. COMPUTING
"""
annotations = extract_annotations(text)
print(annotations)
