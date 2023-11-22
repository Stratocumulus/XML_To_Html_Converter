import os, re, sys
import xml.etree.ElementTree as ET
from xmlToJson import xmlToJson
from xmlToHtml import xmlToHtml
from writeAssessJson import writeAssessJson
"""
TODO:
- in programming problems, xmlToHtml has problem with detecting <label> element
"""

def stringToFilename(input_string):
    """
    Convert string into filename
    i.e replace . - and space
    """
    assert isinstance(input_string, str)

    # Define a translation table to remove spaces, hyphens, and dots
    translator = str.maketrans(" -.", "___", "_")

    # Apply the translation to the input string
    sanitized_string = input_string.translate(translator)

    # Ensure the filename is not empty
    if not sanitized_string:
        sanitized_string = "default_filename"  # Provide a default filename if the input string is empty

    return sanitized_string

def find_first_letter_index(s):
    for index, char in enumerate(s):
        if char.isalpha():
            return index
    return -1  # If no letter is found

def get_substring_to_first_letter(s):
    index = find_first_letter_index(s)
    if index != -1:
        return s[:index]
    else:
        return s 


def fetchProblemFromChapter(chapter_xml_file: str, output_base_directory: str):
    """
    Iterating through xml tree:
    chapter (root)
      |--sequential
            |--vertical
                  |--problem

    then create folders for problems in given output_base_directory
    and convert problems using xmlToHtml(), xmlToJson()

    :param : chapter_xml_file: str, (relative) path to chapter.xml 
    :param : output_base_directory: str, (relative) path to output folder
    """
    verbose = True
    default_attempts = [2,1] # default number of attempts and corresponding points for problems
    given_chapter_number = True
    GIVEN_CHAPTER_NUMBER = "3"

    # Directory containing the local XML files
    sequential_directory = 'sequential'
    vertical_directory = 'vertical'
    problem_directory = 'problem'

    # Parse the main XML file
    tree = ET.parse(chapter_xml_file)
    chapter = tree.getroot()

    # fetch assessment level meta-data
    assessment_title = chapter.attrib['display_name']
    assessment_text = chapter.attrib['highlights'].strip('[]').split(', ')
    assessment_text = '. '.join([s.strip('\'"') for s in assessment_text])

    if verbose:
        print('='*20)
        print("Chapter: ")
        print(chapter.attrib['display_name'])
        print(chapter.attrib['highlights'])

    # Search for which chapter we are processing
    pattern = r'\d{1,2}'
    chapter_number_str = re.search(pattern, chapter.attrib['display_name']).group()
    original_chapter_number = chapter_number_str
    if given_chapter_number:
        chapter_number_str = GIVEN_CHAPTER_NUMBER
    # Search for the first match in the input string
    relative_output_directory = 'c' + original_chapter_number
    output_directory = os.path.join(output_base_directory, relative_output_directory)
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    # now output_directory contains chapter number
    if verbose:
        print("Output Directory: ", output_directory)

    # initialize zones
    zones = []

    # Loop through sequential elements and copy XML files
    for sequential in chapter.findall('sequential'):
        seq_name = sequential.get('url_name')
        seq_path = os.path.join(sequential_directory, f'{seq_name}.xml')
        seq_tree = ET.parse(seq_path)
        seq = seq_tree.getroot()

        # fetch sequential title as sub topic folder name
        sub_topic_number_match = re.search(r'\.(\d{1,2})', seq.attrib['display_name'])
        if sub_topic_number_match:
            sub_topic_number = sub_topic_number_match.group(1)
            sub_topic = 's' + sub_topic_number
        else:
            sub_topic = 'prog'
        sub_topic_directory = os.path.join(output_directory, sub_topic)

        # fetch sequential level meta-data
        seq_in_zone_dict = dict()
        seq_in_zone_dict["title"] = seq.attrib['display_name']
        seq_in_zone_dict["comment"] = f"comment for {seq.attrib['display_name']}"
        seq_in_zone_dict["questions"] = []

        
        if verbose:
            print('-'*20)
            print("sequential: ", seq.attrib['display_name'])
            print("seq source url: ", seq_name)

        for vertical in seq.findall('vertical'):
            vert_name = vertical.get('url_name')
            vert_path = os.path.join(vertical_directory, f'{vert_name}.xml')
            vert_tree = ET.parse(vert_path)
            vert = vert_tree.getroot()

            # fetch vertical level meta-data
            question_title = vert.attrib['display_name']

            if verbose:
                print("vertical: ", vert.attrib['display_name'])
                print("source url: ", vert_name)

            for problem in vert.findall('problem'):
                prob_name = problem.get('url_name')
                prob_path = os.path.join(problem_directory, f'{prob_name}.xml')
                prob_tree = ET.parse(prob_path)
                prob = prob_tree.getroot()
                if verbose:
                    print("problem: ", prob.attrib['display_name'])
                    print("source url: ", prob_name)
                    for child in prob:
                        print(child.tag, child.attrib)
                
                # create current problem output folder
                # prob_folder_name = stringToFilename(+ vert.attrib['display_name'][:2] + '-p' + prob.attrib['display_name'][:2])
                # first_letter_index = find_first_letter_index(seq.attrib['display_name'])
                # if first_letter_index != -1:
                #     substring = get_substring_to_first_letter(seq.attrib['display_name'])
                # else:
                #     substring = seq.attrib['display_name']
                # prob_folder_name = stringToFilename( substring + 'p' + prob.attrib['display_name'][:30])
                prob_folder_name = stringToFilename('p' + prob.attrib['display_name'][:30])
                # drop # : and ,
                characters_to_remove = ['#', ':', ',', '(', ')', '\'', '?']
                for char in characters_to_remove:
                    prob_folder_name = re.sub(re.escape(char), '', prob_folder_name)

                output_prob_path = os.path.join(sub_topic_directory, prob_folder_name)
                output_index = 1
                conflict_flag = False
                while os.path.exists(output_prob_path):
                    output_prob_path = f"{output_prob_path}_{output_index}"
                    output_index += 1
                    conflict_flag = True

                # drop # : and , ?
                characters_to_remove = ['#', ':', ',','(', ')', '\'', '?']
                for char in characters_to_remove:
                    output_prob_path = re.sub(re.escape(char), '', output_prob_path)

                
                os.makedirs(output_prob_path, exist_ok=False)

                # convert .xml file into .json .html (and .py for numerical response problems)
                # sub_question_title = question_title + f": {prob.attrib['display_name']}"
                # sub_question_title = question_title
                sub_question_title = prob.attrib['display_name']
                topic = f"chapter_{original_chapter_number}"
                tags = [f"section_{sub_topic_number}"]
                xmlToJson(question_title=sub_question_title, topic=topic, tags=tags, output_base_directory=output_prob_path, source_url=prob_name)
                xmlToHtml(prob_path=os.path.join(problem_directory, prob_name+'.xml'), output_base_directory=output_prob_path)

                # save problem to zones in infoAssessment.json
                prob_info_dict = dict()
                # if conflict_flag:
                #     prob_info_dict["id"] = relative_output_directory + '/' + prob_folder_name + f'_{output_index}'
                # else:
                prob_info_dict["id"] = relative_output_directory  + '/' + sub_topic  + '/' + prob_folder_name 

                prob_info_dict["points"] = default_attempts
                seq_in_zone_dict['questions'].append(prob_info_dict)
        
        # add current sequential meta-data (problems) into zones
        # add only when current sequential contains problems i.e. not discussion etc.
        if len(seq_in_zone_dict['questions']) > 0:
            zones.append(seq_in_zone_dict)

    # write infoAssessment.json after go through all sequentials
    writeAssessJson(assessment_title=assessment_title, assessment_number=chapter_number_str,
                    zones=zones, assessment_text=assessment_text, output_base_directory=output_directory)



if __name__ == "__main__":
    # chapter_xml_file = 'chapter/c1c0e5a497924a40b800bf69e96b4004.xml'  # Chapter 1
    # chapter_xml_file = 'chapter\966fb80ae3eb485580e7d2cd7c228a87.xml' # 2
    # chapter_xml_file = 'chapter/48f7311ca92b4e2ca5479386627e4a06.xml' # chapter 3
    # chapter\3e19e5b95bcb419da847d32747f25512.xml # 5
    # chapter_xml_file = 'chapter/48ab731aeae546c4aa09ed8fea6f393f.xml' # 6
    # chapter_xml_file = 'chapter/d7812e2686e642ff94abec910a452921.xml' # 9
    # chapter_xml_file = 'chapter\dd20fb91353d4e2c99f866bbf5083218.xml' # 10
    # chapter_xml_file = 'chapter/65aa9d6eea064a57859dd2f2f9e52f62.xml' # 11
    # chapter_xml_file = 'chapter/fafe3692bac9442f85c38bac9a918c0b.xml' # 12


    # chapter_xml_file = 'chapter/2aef3bf02e83479298835e00713e1cef.xml' # 13
    # chapter_xml_file = 'chapter/a24e9e2ae23b49df9cc5cdb4a453ded5.xml' # 14
    # chapter_xml_file = 'chapter/ac30d35b8d51479286e87957d73d69a7.xml' # 15
    # chapter_xml_file = 'chapter/5dbdf3800516442a9fd85581d6efb779.xml' # 16
    chapter_xml_file = 'chapter/812a849be74d480a9696df0ee62e03b8.xml' # 17
    # chapter_xml_file = 'chapter/c1184b73d5a3438fa4dbc86ecbf3bebf.xml'

    output_base_directory = 'converter\output'

    sys.stdout = open('converter/output/terminal_output.txt', 'w')
    fetchProblemFromChapter(chapter_xml_file, output_base_directory)
    
