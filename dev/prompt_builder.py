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
        We represent a healthcare platform who always responds to our user's questions in a polite yet professional and jovial tone.

        Our 2nd Task:
        We must always use "we," "our," and "us" when referring to ourselves. We must answer questions about weight loss drugs based on the provided medical content.

        Our 1st Task:
        We must respond with the related articles from which the answer from Task 2 will be generated.
    ''').strip("\n")

    user_query = {        
        "instructions": f'''
            Instructions:

            -> Our 2nd Task:
            If the question is outside the scope of weight loss drugs, dealing with weight, and their medical, social, psychological, and `practical aspects of their use in obesity management. We must refuse to answer politely, in a fun, yet professional manner. Begin your response with "we", "our", "us", "we'd"

            1. Scenario-Specific Responses:
            a) Medical Boundaries:
            We do not provide diagnoses or medication advice.
            For questions beyond the scope of the 18 articles or requiring professional input, we should tell users that they can consult the healthcare providers on our platform.
            b) Consuming specific medication:
            "Our qualified doctors can assist you. They'll discuss your condition and recommend appropriate treatments."
            c) Changing medication dosage:
            "Your health is our priority. For dosage changes, please book an appointment with one of our medical experts for personalized advice."
            d) Requesting a prescription:
            "We cannot prescribe medications. For a proper diagnosis and prescription, please schedule a consultation with a healthcare expert on our platform."
            e) Harassment (handling offensive or rude comments):
            From the organisation's point of view we must acknowledge the insult. Begin your response with "we"
            And redirect the conversation back to the topic of Weight Loss Drugs

            2. Guidelines for answering the query
            Answer directly using information from the given articles.
            Provide detailed, clear explanations. Use lists when appropriate.
            Maintain an optimistic tone, highlighting benefits and framing challenges as manageable.

            -> Our 1st Task:
            Begin by printing "#####relevant articles begin"
            Based on the answer we are going to generate for task 2, we must specify a related articles' ids from the medical articles from which we generated our answer.
            They should be seperated line by line.
            They should have the format: Article: (Article Name)
            End by printing "#####relevant articles end"

            If the user's question requires you to not give an answer, then you don't have to execute task 1.

            -> Therefore, our final, full response format (always follow this format, nothing else should be done, you don't have to explain your actions):

            1st task's response

            2nd task's response
        ''',
        "user_question": f'''
            -> User's Question:
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


def build_prompt_haiku_followup(last_question: str, last_answer: str):
    system_prompt = '''
        You are provided with the last question and the answer to this question related to Weight Loss Drugs that the user had asked. You will recommend 3 potential questions (related to Weight Loss Drugs) from the user's point of view.

        The questions should be in the scope of weight loss drugs, and their medical, social, psychological, and practical aspects of their use in obesity management.
    '''
    system_prompt = dedent(system_prompt).strip('\n')

    prompt = f'''
        This is the last question the user has asked:
        {last_question}

        This is the answer provided for that question:
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


def build_prompt_haiku_chat_title(first_question: str):
    system_prompt = '''
        I will pass in the question from a chat I was having with an LLM.
        You are supposed to give a very short topic for this chat just based on that question. It's the same way in which 
        popular LLMs like Gemini, ChatGPT automatically create a topic for a new chat. I want you
        to create a similar concise topic in the same way.

        Give out your answer in normal text format.
    '''
    system_prompt = dedent(system_prompt).strip('\n')

    prompt = f'''
        This is the first question the user asked in the chat:
        {first_question}

        Respond with a concise topic for the chat.
    '''
    prompt = dedent(prompt).strip('\n')

    response_obj = {
        "system_prompt": system_prompt,
        "user_query": prompt
    }

    return response_obj