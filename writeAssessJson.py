import xml.etree.ElementTree as ET
import os
import uuid
import json

def writeAssessJson(assessment_title: str, assessment_number: str, zones: list, assessment_text: str, output_base_directory: str):
    """
    Write Assessment level .json, dump meta data from chapter, sequential, and vertical
    """
    assert isinstance(assessment_title, str)
    assert(isinstance(assessment_number, str), "assessment_number needs to be passed as a string")
    assert isinstance(zones, list) # not doing further check
    assert isinstance(assessment_text, str)
    assert isinstance(output_base_directory, str)

    # Constants and Variables
    verbose = False
    ASS_JSON_OUTPUT_FILENAME = "infoAssessment.json"

    # Generate a random UUID (Version 4)
    random_uuid = uuid.uuid4()

    if verbose:
        print('='*20)
        print("Dumping assessment .json metadata")
        print("Random UUID (Version 4):", random_uuid)
        print(f"Assessment Title: {assessment_title}, Number: {assessment_number}")
        print(f"zones: {zones}")
        print("output_base_direactory: ", output_base_directory)

    # write basic informations
    json_output = f"""
{{
    "uuid": "{random_uuid}",
    "type": "Exam",
    "title": "{assessment_title}",
    "set": "Homework",
    "number": "{assessment_number}",
    "multipleInstance": false,
    "shuffleQuestions": false,
    "requireHonorCode": false,
    "autoClose": false,
    "allowAccess": [
        {{
            "mode": "Public",
            "credit": 100,
            "startDate": "2020-09-01T00:00:01",
            "endDate": "2024-09-30T23:59:59"
        }}
    ],
"""

    # add problem to zones
    json_output += "\"zones\": "
    zones_json_string = json.dumps(zones, indent=2)
    json_output += zones_json_string

    ## add assessment description (chapter highlights on EdX)
    if assessment_title is not None:
        json_output +=',\n'
        json_output += f"""
    "text": "<p>{assessment_text}</p>"
}}
"""
    # print(json_output)

    with open(os.path.join(output_base_directory, ASS_JSON_OUTPUT_FILENAME), "w", encoding="utf-8") as ass_json_file:
        ass_json_file.write(json_output)


if __name__ == "__main__":
    assessment_title = "Sample Assessment Title"
    assessment_number = "1"
    zones = [{   
                "title": "Zone 1 title",
                "comment": "Zone 1 comment",
                "questions": [
                    {   
                        "id": "Testcase1",
                        "points": [2,1]
                    }
                ]
            },
            {
                "title": "Zone 2 title",
                "comment": "Zone 2 comment",
                "questions": [
                    {   
                        "id": "Testcase2",
                        "points": [2,1]
                    }
                    ]
            }]

    assessment_text = "chapter highlights texts"
    output_base_directory = "converter\output"
    
    writeAssessJson(assessment_title, assessment_number, zones, assessment_text, output_base_directory)