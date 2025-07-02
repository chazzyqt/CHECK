import re

def match_annotations(full_data, final_annot):
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
        # Check if the current annotation matches the text in the item
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

# Example usage
final_annot = ['1.', '1.', '6.', '2.', '7.', '3.', '8.', '4.', '9.', '5.', '10.', '2.', '1.', '6.', '11.', '2.', '7.', '12.', '3.', '8.', '13.', '4.', '9.', '14.', '5.', '10.', '15.', '3.', '1.', '6.', '2.', '7.', '3.', '8.', '4.', '9.', '5.', '10.']
full_data = [{'box': (509, 105, 543, 129), 'text': 'De'}, {'box': (545, 105, 577, 129), 
'text': 'La'}, {'box': (577, 105, 637, 131), 'text': 'Salle'}, {'box': (637, 105, 751, 133), 'text': 'University'}, {'box': (750, 108, 776, 129), 'text': '-'}, {'box': (772, 103, 907, 129), 'text': 'Dasmaninas'}, {'box': (425, 129, 541, 155), 'text': 'COLLEGE'}, {'box': (541, 127, 583, 157), 'text': 'OF'}, {'box': (581, 129, 686, 155), 'text': 'SCIENCE'}, {'box': (686, 129, 742, 155), 'text': 'AND'}, {'box': (742, 129, 877, 155), 'text': 'COMPUTER'}, {'box': (879, 129, 982, 155), 'text': 'STUDIES'}, {'box': (500, 157, 637, 181), 'text': 'COMPUTER'}, {'box': (637, 155, 744, 181), 'text': 'SCIENCE'}, {'box': (744, 155, 909, 181), 'text': 'DEPARTMENT'}, {'box': (433, 183, 549, 208), 'text': 'Summerive'}, {'box': (549, 183, 680, 208), 'text': 'Examination'}, {'box': (680, 183, 705, 208), 'text': 'in'}, {'box': (705, 183, 834, 210), 'text': 'subjectCode'}, {'box': (830, 189, 855, 208), 'text': '-'}, {'box': (849, 183, 986, 210), 'text': 'subjectName'}, {'box': (273, 226, 367, 260), 'text': 'NAME:'}, {'box': (388, 219, 487, 262), 'text': 'JOHN'}, {'box': (506, 223, 590, 260), 'text': 'DOE'}, {'box': (727, 230, 834, 258), 'text': 'SCORE:'}, {'box': (270, 279, 354, 313), 'text': 'DATE:'}, {'box': (390, 273, 562, 315), 'text': 'NOVEMBER'}, {'box': (564, 273, 673, 311), 'text': '212014'}, {'box': (727, 283, 870, 309), 
'text': 'PROGRAM'}, {'box': (875, 283, 965, 311), 'text': 'CODE:'}, {'box': (984, 268, 1113, 313), 'text': 'BCS42'}, {'box': (270, 384, 348, 418), 'text': 'TEST'}, {'box': (358, 388, 384, 416), 'text': '1.'}, {'box': (386, 386, 562, 418), 'text': 'Identication'}, {'box': (564, 388, 609, 421), 'text': '(20'}, {'box': (611, 386, 673, 423), 'text': 'pts.)'}, {'box': (348, 440, 380, 474), 'text': '1.'}, {'box': (448, 435, 555, 478), 'text': 'DATA'}, {'box': (774, 440, 810, 476), 'text': '6.'}, {'box': (832, 433, 1001, 476), 'text': 'COMPUTER'}, {'box': (350, 493, 376, 523), 'text': '2.'}, {'box': (438, 485, 600, 526), 'text': 'SCIENCE'}, {'box': (776, 493, 808, 526), 'text': '7.'}, {'box': (864, 485, 933, 526), 'text': 'RAM'}, {'box': (348, 543, 380, 577), 'text': '3.'}, {'box': (423, 532, 570, 573), 'text': 'MACHINE'}, {'box': (573, 536, 716, 571), 'text': 'LEARNING'}, {'box': (774, 545, 808, 579), 'text': '8.'}, {'box': (855, 536, 961, 579), 'text': 'DBMS'}, {'box': (346, 596, 380, 630), 'text': '4.'}, {'box': (408, 586, 526, 630), 'text': 'NEURAL'}, {'box': (540, 590, 678, 626), 'text': 'NETWORK'}, {'box': (774, 596, 808, 631), 'text': '9.'}, {'box': (845, 588, 1012, 624), 'text': 'LANGUAGE'}, {'box': (348, 646, 380, 680), 'text': '5.'}, {'box': (429, 639, 560, 680), 'text': 'THESIS'}, {'box': (761, 650, 806, 
680), 'text': '10.'}, {'box': (841, 639, 922, 678), 'text': 'DATA'}, {'box': (922, 641, 1008, 678), 'text': 'BASE'}, {'box': (253, 751, 333, 785), 'text': 'TEST'}, {'box': (341, 755, 367, 783), 'text': '2.'}, {'box': (371, 755, 495, 789), 'text': 'Matching'}, {'box': (496, 753, 566, 791), 'text': 'Type'}, {'box': (568, 755, 613, 789), 'text': '(15'}, {'box': (613, 755, 676, 791), 'text': 'pts.)'}, {'box': (348, 808, 380, 841), 'text': '1.'}, {'box': (397, 802, 433, 836), 'text': 'A'}, {'box': (547, 808, 581, 841), 'text': '6.'}, {'box': (585, 798, 620, 836), 'text': 'F'}, {'box': (738, 808, 781, 843), 'text': '11.'}, {'box': (791, 800, 823, 836), 'text': 'K'}, {'box': (348, 858, 380, 892), 'text': '2.'}, {'box': (405, 851, 429, 877), 'text': 'B'}, {'box': (547, 860, 585, 894), 'text': '7.'}, {'box': (583, 855, 620, 886), 'text': 'G'}, {'box': (738, 860, 780, 892), 'text': '12.'}, {'box': (796, 853, 821, 883), 'text': 
'L'}, {'box': (348, 909, 380, 943), 'text': '3.'}, {'box': (393, 905, 433, 937), 'text': 'c'}, {'box': (543, 903, 633, 948), 'text': 
'8.14'}, {'box': (738, 913, 781, 945), 'text': '13.'}, {'box': (796, 900, 821, 933), 'text': 'M'}, {'box': (348, 961, 380, 995), 'text': '4.'}, {'box': (390, 956, 438, 995), 'text': 'D'}, {'box': (547, 961, 583, 995), 'text': '9.'}, {'box': (590, 956, 622, 990), 'text': 'I'}, {'box': (736, 963, 781, 995), 'text': '14.'}, {'box': (791, 954, 823, 990), 'text': 'N'}, {'box': (346, 1012, 380, 1048), 
'text': '5.'}, {'box': (397, 1008, 436, 1044), 'text': 'E'}, {'box': (541, 1016, 586, 1048), 'text': '10.'}, {'box': (592, 1008, 628, 1042), 'text': 'J'}, {'box': (736, 1016, 780, 1048), 'text': '15.'}, {'box': (795, 1010, 821, 1038), 'text': '0'}, {'box': (254, 1121, 331, 1149), 'text': 'TEST'}, {'box': (341, 1121, 371, 1151), 'text': '3.'}, {'box': (378, 1121, 425, 1151), 'text': 'Fill'}, {'box': (425, 1123, 455, 1149), 'text': 'in'}, {'box': (457, 1123, 504, 1151), 'text': 'the'}, {'box': (508, 1123, 596, 1151), 'text': 'blanks'}, {'box': (600, 1123, 643, 1155), 'text': '(10'}, {'box': (645, 1121, 706, 1156), 'text': 'pts.)'}, {'box': (348, 1173, 380, 1207), 'text': '1.'}, {'box': (410, 1164, 611, 1205), 'text': 'ALGORITHM'}, {'box': (770, 1173, 804, 1207), 'text': '6.'}, {'box': (841, 1160, 1038, 1203), 'text': 'PARALLELISM'}, {'box': (346, 1224, 378, 1258), 'text': '2.'}, {'box': (423, 1213, 596, 1254), 'text': 'COMPILER'}, {'box': (770, 1226, 804, 1258), 'text': '7.'}, {'box': (856, 1215, 980, 1258), 'text': 'QUERY'}, {'box': (346, 1275, 380, 1310), 'text': '3.'}, {'box': (395, 1265, 474, 1310), 'text': 'DATA'}, {'box': (478, 1269, 631, 1305), 'text': 'STRUCTURE'}, {'box': (770, 1275, 802, 1308), 'text': '8.'}, {'box': (853, 1267, 1008, 1303), 'text': 'HASHING'}, {'box': (345, 1327, 378, 1361), 'text': 
'4.'}, {'box': (435, 1321, 609, 1355), 'text': 'RECURSION'}, {'box': (770, 1327, 802, 1361), 'text': '9.'}, {'box': (873, 1318, 988, 
1353), 'text': 'MODEL'}, {'box': (348, 1381, 378, 1411), 'text': '5.'}, {'box': (466, 1368, 547, 1404), 'text': 'APII'}, {'box': (757, 1380, 802, 1410), 'text': '10.'}, {'box': (853, 1366, 1059, 1408), 'text': 'COMPUTING'}]
result = match_annotations(full_data, final_annot)
#print(result[-1]['number'])

tests = [
    {
        'test_number': 1,
        'test_type': 'Identification',
        'total_points': 20,
        'correct_points': None,
        'full_text': '1. DATA 6. COMPUTER 2. SCIENCE 7. RAM 3. MACHINE LEARNING 8. DBMS 4. NEURAL NETWORK 9. LANGUAGE 5. THESIS 10. DATA BASE',
        'question_answer_pairs': [
            {'question_number': 1, 'answer': 'DATA'},
            {'question_number': 2, 'answer': 'SCIENCE'},
            {'question_number': 3, 'answer': 'MACHINELEARNING'},
            {'question_number': 4, 'answer': 'NEURALNETWORK'},
            {'question_number': 5, 'answer': 'THESIS'},
            {'question_number': 6, 'answer': 'COMPUTER'},
            {'question_number': 7, 'answer': 'RAM'},
            {'question_number': 8, 'answer': 'DBMS'},
            {'question_number': 9, 'answer': 'LANGUAGE'},
            {'question_number': 10, 'answer': 'DATABASE'}
        ]
    },
    {

    'test_number':2,
    'test_type':'Matching Type',
    'total_points':15,
    'correct_points':None,
    'full_text':'1. A 6. F 11. K 2. B 7. G 12. L 3. c 8.14 13. M 4. D 9. I 14. N 5. E 10. J 15. 0',
    'question_answer_pairs':[
        {
            'question_number':1,
            'answer':'A'
        },
        {
            'question_number':2,
            'answer':'B'
        },
        {
            'question_number':3,
            'answer':'C'
        },
        {
            'question_number':4,
            'answer':'D'
        },
        {
            'question_number':5,
            'answer':'E'
        },
        {
            'question_number':6,
            'answer':'F'
        },
        {
            'question_number':7,
            'answer':'G'
        },
        {
            'question_number':8,
            'answer':'14'
        },
        {
            'question_number':9,
            'answer':'I'
        },
        {
            'question_number':10,
            'answer':'J'
        },
        {
            'question_number':11,
            'answer':'K'
        },
        {
            'question_number':12,
            'answer':'L'
        },
        {
            'question_number':13,
            'answer':'M'
        },
        {
            'question_number':14,
            'answer':'N'
        },
        {
            'question_number':15,
            'answer':'0'
        }
    ]

},
{

    'test_number':3,
    'test_type':'Fill in the blanks',
    'total_points':10,
    'correct_points':None,
    'full_text':'1. ALGORITHM 6. PARALLELISM 2. COMPILER 7. QUERY 3. DATA STRUCTURE 8. HASHING 4. RECURSION 9. MODEL 5. APII 10. COMPUTING',
    'question_answer_pairs':[
        {
            'question_number':1,
            'answer':'ALGORITHM'
        },
        {
            'question_number':2,
            'answer':'COMPILER'
        },
        {
            'question_number':3,
            'answer':'DATASTRUCTURE'
        },
        {
            'question_number':4,
            'answer':'RECURSION'
        },
        {
            'question_number':5,
            'answer':'APII'
        },
        {
            'question_number':6,
            'answer':'PARALLELISM'
        },
        {
            'question_number':7,
            'answer':'QUERY'
        },
        {
            'question_number':8,
            'answer':'HASHING'
        },
        {
            'question_number':9,
            'answer':'MODEL'
        },
        {
            'question_number':10,
            'answer':'COMPUTING'
        }
    ]

}
]



def sort_by_annotation(section):
    return sorted(section, key=lambda x: float(x['annotation'].replace('.', '')))


currentNumber = 1
annot = []
for item in tests:
    if currentNumber == 1: 
        print(currentNumber,"before")
        #print(len(item['question_answer_pairs']))
        number_of_questions = len(item['question_answer_pairs'])
        section = sort_by_annotation(result[currentNumber: currentNumber+number_of_questions])
        currentNumber = currentNumber + number_of_questions
        annot.append(section)
        print(currentNumber, "this is the current number")
    else:
        print(currentNumber, "before")
        number_of_questions = len(item['question_answer_pairs'])
        section = sort_by_annotation(result[currentNumber+1: currentNumber+1+number_of_questions])
        currentNumber =  currentNumber + 1 + number_of_questions
        annot.append(section)
        print(currentNumber, "this is the current number")


currentCount = 0
for test, annotation in zip(tests, annot):
    currentCount +=1
    print(annotation)
    for pair, boxes in zip(test["question_answer_pairs"], annotation):
         
          pair['annotation'] = boxes["box"]
          

print(tests)
