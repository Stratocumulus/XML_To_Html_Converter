import os
import xml.etree.ElementTree as ET

def xmlToHtml(prob_path: str, output_base_directory: str):
    """
    Dumps problem descriptions into .html file
    """
    assert isinstance(prob_path, str)
    assert isinstance(output_base_directory, str)

    #Constants and Variables:
    SHOW_HINT_AFTER = "1"
    verbose = False
    HTML_OUTPUT_FILENAME = "question.html"
    PYTHON_OUTPUT_FILENAME = "server.py"

    # load xml data
    prob_tree = ET.parse(prob_path)
    root = prob_tree.getroot()

    element_tags = []
    for child in root:
        element_tags.append(child.tag)
    if verbose:
        print(element_tags)

    # if the problem is multichoice problem
    if "multiplechoiceresponse" in element_tags or "choiceresponse" in element_tags:
        # Determine question format
        assert("multiplechoiceresponse" not in element_tags and 
            "choiceresponse" not in element_tags, "Two types of choices conflict.")
        if "multiplechoiceresponse" in element_tags:
            problem_format = "multiple-choice"
        if "choiceresponse" in element_tags:
            problem_format = "checkbox"

        # Extract relevant data from XML
        question_element = root.find(".//p") # root.find() will find the first element
        label_element = root.find(".//label")

        choices = root.findall(".//choice")
        hints = root.findall(".//hint")
        explanations = root.find(".//div[@class='detailed-solution']")

        # Generate HTML based on the extracted data
        html_output = ""
        if label_element is not None:
            label_text = ET.tostring(label_element, encoding="unicode")
            html_output += f"""
<pl-question-panel>
<p>{label_text}</p>
</pl-question-panel>
""" 

            html_output += f"""
<div class="card-body">
    <pl-{problem_format} answers-name="multichoice_1" fixed-order=true partial-credit=true>
""" # fix the order of choices

        elif question_element is not None:
            
            question_paragraphs = []

            for element in question_element.iter():
                if element.tag == 'p':
                    question_paragraphs.append(element.text)
                else:
                    break  # Stop when a non-<p> element is encountered

            html_output += f"""
<pl-question-panel>
"""         

            for paragraph in question_paragraphs:
                html_output += f"""
<p>{paragraph}</p>
"""
            html_output += f"""
</pl-question-panel>
"""


        html_output += f"""
<div class="card-body">
    <pl-{problem_format} answers-name="multichoice_1" fixed-order=true partial-credit=true>
"""
    



        # parse the choices
        for choice in choices:
            is_correct = "true" if choice.get("correct") == "true" else "false"
            choice_text = choice.text.strip()
            html_output += f"      <pl-answer correct=\"{is_correct}\">{choice_text}</pl-answer>\n"

        html_output += f"""
    </pl-{problem_format}>
</div>

"""
        # if there are any hint to this problem
        # parse them to the end of the problem
        if len(hints) > 0:
            html_output += """
<pl-hidden-hints>
"""
            for hint in hints:
                hint_text = hint.text.strip()
                html_output += f"""
    <pl-hint show-after-submission={SHOW_HINT_AFTER}>
    {hint_text}
    </pl-hint>
"""     
            html_output += """
</pl-hidden-hints>
"""

        # if there are explanations to this problem
        # parse them to the end of the problem
        if explanations is not None:
            html_output += """
<pl-answer-panel>
    <div class="detailed-solution"> 
"""
            for explanation in explanations:
                explanation_text = explanation.text.strip()
                html_output += f"""
    <p>{explanation_text}</p>
"""     

            html_output += """
    </div>
</pl-answer-panel>
"""
        
        # dump output file
        with open(os.path.join(output_base_directory, HTML_OUTPUT_FILENAME), "w", encoding="utf-8") as html_file:
            html_file.write(html_output)

    # else if the problem requires numerical response
    elif "numericalresponse" in element_tags:
        # Extract relevant data from XML
        main_question_text = root.find(".//p").text.strip()
        numresponses = root.findall(".//numericalresponse")
        uls = root.findall(".//ul")
        hints = root.findall(".//hint")
        explanations = root.findall(".//div[@class='detailed-solution']")
        label_element = root.find(".//label")

        # initialize outputs
        html_output = ""
        if label_element is not None:
            html_output = f"""
    <pl-question-panel>
    <p>{ET.tostring(label_element, encoding="unicode")}</p>
    </pl-question-panel>
    """
        elif main_question_text is not None:

            question_paragraphs = []
            start_iteration = False
            for element in root.iter():
                if element.tag == 'p':
                    start_iteration = True
                if start_iteration:
                    if element.tag == 'p':
                        question_paragraphs.append(element.text)
                    else:
                        break
            html_output += f"""
<pl-question-panel>
"""         
            for paragraph in question_paragraphs:
                html_output += f"""
<p>{paragraph}</p>
"""
            html_output += f"""
</pl-question-panel>
"""
        py_output = f"""
def generate(data):
"""
        # if there is only single numerical responses
        if len(numresponses) == 1:
            if verbose:
                print("case 1: 1 numerical response")

            html_output += f"""
<div class="card my-2">
    <div class="card-body">
        <pl-number-input answers-name="ans" label="$ans=$" rtol="1e-2" atol="1e-2"></pl-number-input>
    </div>
</div>
"""     
            py_output += f"""
    data["correct_answers"]["ans"] = {numresponses[0].attrib["answer"]}
"""
        # if there are multiple numerical responses
        # see problem problem\3764d3faa7694190a9af35862fc57b95.xml
        elif len(numresponses) > 1 and len(uls) == len(numresponses) and len(uls) > 0:
            if verbose:
                print("case 2: multi numerical, has uls")
            num_of_responses = len(numresponses)
            for idx in range(num_of_responses):
                # locate <li> inside <ul>
                assert("li_inside_ul_doesnot_exist", uls[idx].findall("./*"))
                sub_question_text = uls[idx][0].text.strip()
                sub_question_ans = numresponses[idx].attrib["answer"]
                if verbose:
                    print(sub_question_text)
                    print(numresponses[idx].attrib["answer"])
                html_output += f"""
<div class="card my-2">
    <div class="card-body">
        <pl-question-panel>
        <p> {sub_question_text} </p>
        </pl-question-panel>
        <pl-number-input answers-name="ans_{idx+1}" label="$ans_{idx+1}=$" rtol="1e-2" atol="1e-2"></pl-number-input>
    </div>
</div>
"""         
                py_output += f"""
    data["correct_answers"]["ans_{idx+1}"] = {sub_question_ans}
"""
        # if there are no uls
        # see problem problem\7b78dc044afd491a8d840ef6a0f2353e.xml
        elif len(numresponses) > 1 and  len(uls) != len(numresponses):
            idx = 0
            sub_question_ans = None
            sub_question_text = ""
            read_p_label = False
            if verbose:
                print("case 3: multiple numericals, some uls")
            for element in root.iter():
                # print(element.tag)
                if element.tag == 'numericalresponse':
                    html_output += f"""
<div class="card my-2">
    <div class="card-body">
        <pl-question-panel>
        <p> {sub_question_text} </p>
        </pl-question-panel>
        <pl-number-input answers-name="ans_{idx+1}" label="$ans_{idx+1}=$" rtol="1e-2" atol="1e-2"></pl-number-input>
    </div>
</div>
"""                 
                    sub_question_ans = element.attrib["answer"]
                    py_output += f"""
    data["correct_answers"]["ans_{idx+1}"] = {sub_question_ans}
"""
                    idx += 1
                    sub_question_text = ""
                    read_p_label = True

                if element.tag == 'p' and read_p_label:
                        sub_question_text += element.text.strip()
                        sub_question_text += ' '


        else:
            print("case 4: *** undefined case ***")

        # if there are any hints to this problem
        # parse them to the end of the problem
        if len(hints) > 0:
            html_output += """
<pl-hidden-hints>
"""
            for hint in hints:
                hint_text = hint.text
                if len(hint_text.strip()) == 0:
                    for element in hint:
                        hint_text += element.text.strip()
                html_output += f"""
<pl-hint show-after-submission={SHOW_HINT_AFTER}>
{hint_text}
</pl-hint>
"""
            html_output += """
</pl-hidden-hints>
"""

        # if there are explanations to this problem
        # parse them to the end of the problem
        if explanations is not None:
            for explanation in explanations:
                html_output += """
<pl-answer-panel>
    <div class="detailed-solution">
"""         
                for element in explanation:
                    if element.text is not None:
                        explanation_text = element.text.strip()
                        html_output += f"""
    <p>{explanation_text}</p>
"""     

                html_output += """
    </div>
</pl-answer-panel>
"""
        # dump output file
        with open(os.path.join(output_base_directory, HTML_OUTPUT_FILENAME), "w", encoding="utf-8") as html_file:
            html_file.write(html_output)
        with open(os.path.join(output_base_directory, PYTHON_OUTPUT_FILENAME), "w", encoding="utf-8") as py_file:
            py_file.write(py_output)

if __name__ == "__main__":
    
    # prob_path = "problem/23fdec6639244a5b89ec47cbb45e4690.xml" # multiplechoiceresponse
    # prob_path = "problem/c1f3c02c62ec495fa469a2d9667915a8.xml" # choiceresponse (checkbox)
    # prob_path = "problem/c679b7a2b98e452bbc045fa054930402.xml" # single numresponse
    # prob_path = "problem/1c980d07a6bd4827a7b80a15a71e8033.xml" # multi numresponse
    # prob_path = "problem/e18698bbf13c418cb1f0dee6e39be6dd.xml" # multi multichoice
    # prob_path = "problem/7b78dc044afd491a8d840ef6a0f2353e.xml" # multi problem discription
    # prob_path = "problem/0a48cdaf965c4986a3bba7a2be694ee4.xml" # multi explanation tabs
    # prob_path = "problem/2ebdb6e8d5fb4833bcd0bc0de7d0787a.xml" # multi problem description inside question tab
    # prob_path = "problem/5f15c73284a94eba8432c9ea43d672b3.xml" # cannot get hint for numerical problems, when hint wrapped by <div>
    # TODO
    # why this one gets <label> inside <p>
    # converter\output\assessment_2\12_7_p2\question.html
    
    prob_path = "problem/d1138700044f4f48879c47f0c35984c6.xml" # problem description gets previous explanation


    # prob_path = "problem/6ea9c88daf00404c8ac0018c4860dcda.xml" # programming problem

    output_base_directory = 'converter\output'
    xmlToHtml(prob_path, output_base_directory)


"""
TODO: 
It would be better to first convert the Chapter 1 problems

1. <code> inside <p> is un-converted
- NA
"""