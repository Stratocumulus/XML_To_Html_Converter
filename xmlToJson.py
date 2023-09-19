import xml.etree.ElementTree as ET
import os
import uuid

def xmlToJson(question_title: str, topic: str, tags: list, output_base_directory: str):
    """
    Dump meta data to problem .json file
    """
    assert isinstance(question_title, str)
    assert isinstance(topic, str)
    assert isinstance(tags, list)
    assert(len(tags) > 0, "need to give at least one tag")
    for tag in tags:
        assert isinstance(tag, str)
    assert isinstance(output_base_directory, str)
    
    # Constants and Variables
    verbose = False
    JSON_OUTPUT_FILENAME = "info.json"


    # Generate a random UUID (Version 4)
    random_uuid = uuid.uuid4()
    if verbose:
        print('-'*10)
        print("Dumping .json metadata")
        print("Random UUID (Version 4):", random_uuid)
        print("Question Title: ", question_title)
        print(f"topic: {topic}, tags: {tags}")
        print("output_base_direactory: ", output_base_directory)

    # add uuid, title, and topic
    json_output = """
{
"""
    json_output += f"""
    "uuid": "{random_uuid}",
    "title": "{question_title}",
    "topic": "{topic}",
"""

    # add tags
    if len(tags) > 0:
        json_output += """
    "tags": [
"""
        for tag in tags:
            # last tag no comma
            if tag is tags[-1]:
                json_output += f"""
    "{tag}"
"""
                break
            json_output += f"""
    "{tag}",
"""
        json_output += """
    ],
"""

    json_output += """
    "type": "v3"
}
"""

    with open(os.path.join(output_base_directory, JSON_OUTPUT_FILENAME), "w", encoding="utf-8") as json_file:
        json_file.write(json_output)

if __name__ == "__main__":
    # sample kwargs
    question_title = "sample_title"
    topic = "hw1"
    tags = ["chapter_1"]
    output_base_directory = "converter\output"
    xmlToJson(question_title, topic, tags, output_base_directory)
