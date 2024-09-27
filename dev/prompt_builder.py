from typing import List
import json
from textwrap import dedent

def get_articles():
    with open("articles.json", mode="r", encoding="utf-8") as read_file:
        json_data = json.load(read_file)
        return json_data

def line_by_line(queries: List[str]):
    # print(queries)
    data = ''
    for _ in filter(None, queries):
        data += _
        data += '\n'
        # print('line by line', data)
    return data

def build_prompt(query: str):
    # print(user_queries)
    prompt = f"""

This is the user's current query:
{query}

Answer the user's current query by taking into context all the content from the text file. If the user's query just contains a greeting, then simply just respond with a small greeting.
"""
    return prompt


def build_prompt_flash(user_queries: List[str]):
    prompt = f'''
These are the questions the user has previously asked:
{line_by_line(user_queries)}


'''
    prompt += '''
Response JSON Schema:
    response = {
        "questions": list[str]
    }

Return a `response`
do not enclose your json with "```json ```"
'''
    return prompt


def build_prompt_sonnet(query: str):
    book_file_path = './Google_docs_extract_data.txt'
    with open(book_file_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
    book_data = ''.join(lines)

    system_prompt = dedent('''
    You are an empathetic medical chat bot representing a healthcare platform. You must always use "we," "our," and "us" when referring to yourself or the platform. Answer questions about weight loss drugs based on 18 provided articles. Adhere to these guidelines:

    1. Response Approach:

    Answer directly using information from the given articles.
    Provide detailed, clear explanations. Use lists when appropriate.
    Maintain an optimistic tone, highlighting benefits and framing challenges as manageable.
    Always use "we," "our," and "us" to refer to yourself and the platform.


    2. Medical Boundaries:

    Do not provide diagnoses or medication advice.
    For questions beyond the scope of the 18 articles or requiring professional input, refer users to healthcare providers on our platform.


    3. Scenario-Specific Responses:
    a) Consuming specific medication:
    "Our qualified doctors can assist you. They'll discuss your condition and recommend appropriate treatments."
    b) Changing medication dosage:
    "Your health is our priority. For dosage changes, please book an appointment with one of our medical experts for personalized advice."
    c) Requesting a prescription:
    "We cannot prescribe medications. For a proper diagnosis and prescription, please schedule a consultation with a healthcare expert on our platform."
    d) Harassment (offensive language):
    "We understand you might be frustrated, but we can't engage with inappropriate language. Would you like to rephrase your question respectfully?"
    Language Use:

    4. Always use plural pronouns (we, our, us) when referring to yourself or the platform.
    Example: "We recommend..." instead of "I recommend..."
    Example: "Our platform offers..." instead of "My platform offers..."
    ''').strip("\n")

    user_query = query    
    
    return_obj = {
        "system_prompt": system_prompt,
        "user_query": user_query,
        "book_data": book_data
    }

    return return_obj


def build_prompt_haiku(user_queries: List[str]):
    system_prompt = "You are provided with a list of questions related to Weight Loss Drugs, that the user had asked till now. You will recommend 3 potential questions(related to Weight Loss Drugs) from the user's point of view."

    prompt = f'''
        These are the questions the user has previously asked:
        {line_by_line(user_queries)}

        output in JSON format with keys: "questions" (list).
    '''
    prompt = dedent(prompt).strip('\n')

    response_obj = {
        "system_prompt": system_prompt,
        "user_query": prompt 
    }

    return response_obj