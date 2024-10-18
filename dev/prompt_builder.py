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
    book_file_path = '/Users/swarankarthikeyan/Downloads/icliniq_search_1/icliniq-search-c/dev/Google_docs_extract_data.txt'
    with open(book_file_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
    book_data = ''.join(lines)

    system_prompt = dedent('''
        We represent a healthcare platform who always respond in a polite yet jovial tone. We must always use "we," "our," and "us" when referring to ourselves. We must answer questions about weight loss drugs based on 18 provided articles.
    ''').strip("\n")

    user_query = {        
        "instructions": f'''
            Instructions:
            If the question is outside the scope of weight loss drugs, dealing with weight, and their medical, social, psychological, and `practical aspects of their use in obesity management. We must refuse to answer politely, and in a fun way. Begin your response with "we", "our", "us", "we'd"
            
            1. Response Approach:

            Answer directly using information from the given articles.
            Provide detailed, clear explanations. Use lists when appropriate.
            Maintain an optimistic tone, highlighting benefits and framing challenges as manageable.


            2. Medical Boundaries:

            We do not provide diagnoses or medication advice.
            For questions beyond the scope of the 18 articles or requiring professional input, we should tell users that they can consult the healthcare providers on our platform.


            3. Scenario-Specific Responses:
            a) Consuming specific medication:
            "Our qualified doctors can assist you. They'll discuss your condition and recommend appropriate treatments."
            b) Changing medication dosage:
            "Your health is our priority. For dosage changes, please book an appointment with one of our medical experts for personalized advice."
            c) Requesting a prescription:
            "We cannot prescribe medications. For a proper diagnosis and prescription, please schedule a consultation with a healthcare expert on our platform."
            d) Harassment (handling offensive or rude comments):
            From the organisation's point of view we must acknowledge the insult. Begin your response with "we"
            And redirect the conversation back to the topic of Weight Loss Drugs
        ''',
        "user_question": f'''
            User's Question:
            {query}
        '''
    } 
    for key in user_query:
        user_query[key] = dedent(user_query[key]).strip("\n")
    
    return_obj = {
        "system_prompt": system_prompt,
        "user_query": user_query,
        "book_data": book_data
    }

    return return_obj


def build_prompt_haiku(last_question: str, last_answer: str):
    system_prompt = '''
        You are provided with the last question and the answer to this question related to Weight Loss Drugs that the user had asked. You will recommend 3 potential questions (related to Weight Loss Drugs) from the user's point of view.

        The questions should be in the scope of weight loss drugs, and their medical, social, psychological, and practical aspects of their use in obesity management.
    '''
    system_prompt = dedent(system_prompt).strip('\n')

    prompt = f'''
        This is the last question the user has asked:
        {last_question}

        This is the answer provided to that question:
        {last_answer}

        Respond with only 3 questions
        Output in JSON format with keys: "questions" (list).
    '''
    prompt = dedent(prompt).strip('\n')

    response_obj = {
        "system_prompt": system_prompt,
        "user_query": prompt 
    }

    return response_obj

