import os
import xml.etree.ElementTree as ET

def xmlToHtml(prob_path: str, output_base_directory: str):
    """
    Dumps problem descriptions into .html file
    """
    assert isinstance(prob_path, str)
    assert isinstance(output_base_directory, str)

    #Constants and Variables:
    SHOW_HINT_AFTER = "2"
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
            print(label_text)
            html_output += f"""
<pl-question-panel>
<p>{label_text}</p>
</pl-question-panel>
""" 
            html_output += f"""
<div class="card-body">
    <pl-{problem_format} answers-name="multichoice_1">
"""

        elif question_element is not None:
            html_output += f"""
<pl-question-panel>
<p>{question_element.text.strip()}</p>
</pl-question-panel>
""" 
        html_output += f"""
<div class="card-body">
    <pl-{problem_format} answers-name="multichoice_1">
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
        explanations = root.find(".//div[@class='detailed-solution']")

        label_element = root.find(".//label")

        # initialize outputs
        if label_element is not None:
            html_output = f"""
    <pl-question-panel>
    <p>{ET.tostring(label_element, encoding="unicode")}</p>
    </pl-question-panel>
    """
        elif main_question_text is not None:

            html_output = f"""
    <pl-question-panel>
    <p>{main_question_text}</p>
    </pl-question-panel>
    """
        py_output = f"""
def generate(data):
"""
        # if there is only single numerical responses
        if len(numresponses) == 1:
            html_output += f"""
<div class="card my-2">
    <div class="card-body">
        <pl-number-input answers-name="ans" label="$ans=$"></pl-number-input>
    </div>
</div>
"""     
            py_output += f"""
    data["correct_answers"]["ans"] = {numresponses[0].attrib["answer"]}
"""
        # if there are multiple numerical responses
        elif len(numresponses) > 1 and len(uls) == len(numresponses):
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
        <pl-number-input answers-name="ans_{idx+1}" label="$ans_{idx+1}=$"></pl-number-input>
    </div>
</div>
"""         
                py_output += f"""
    data["correct_answers"]["ans_{idx+1}"] = {sub_question_ans}
"""
        # if there are any hints to this problem
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
        with open(os.path.join(output_base_directory, PYTHON_OUTPUT_FILENAME), "w", encoding="utf-8") as py_file:
            py_file.write(py_output)

if __name__ == "__main__":
    
    # prob_path = "problem/23fdec6639244a5b89ec47cbb45e4690.xml" # multiplechoiceresponse
    # prob_path = "problem/c1f3c02c62ec495fa469a2d9667915a8.xml" # choiceresponse (checkbox)
    # prob_path = "problem/c679b7a2b98e452bbc045fa054930402.xml" # single numresponse
    # prob_path = "problem/1c980d07a6bd4827a7b80a15a71e8033.xml" # multi numresponse

    prob_path = "problem/6ea9c88daf00404c8ac0018c4860dcda.xml" # programming problem

    output_base_directory = 'converter\output'
    xmlToHtml(prob_path, output_base_directory)


"""
TODO: 
It would be better to first convert the Chapter 1 problems

6. convert other elements than problems
- NA
"""