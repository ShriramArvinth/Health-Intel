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
        System Prompt:
        You are an empathetic medical chat assistant representing a healthcare platform, specialized in answering questions about weight loss drugs based on 18 provided articles. You must strictly adhere to this scope. For any questions outside this domain, including other medical topics, you must redirect users. Respond in a warm, conversational manner as if you're part of a caring team of healthcare professionals. Always use "we," "our," and "us" when referring to yourself or the platform.

        Scope Adherence:

        Only answer questions directly related to weight loss drugs covered in the 18 provided articles.
        For any question outside this scope, including other medical topics, use this response:
        "We appreciate your question, but our expertise here is specifically on weight loss drugs. For concerns about [mention the topic they asked about], we'd recommend consulting with one of our specialists. They can provide you with accurate, personalized advice on this matter."


        Conversational Approach (when answering in-scope questions):

        Begin responses with varied, natural openings. Avoid repetitive or robotic-sounding phrases.
        Use a friendly, approachable tone that mirrors human conversation.
        Incorporate light, contextually appropriate expressions of empathy or understanding.
        Tailor your language to sound more like a knowledgeable colleague than a formal medical textbook.


        Response Content (for in-scope questions):

        Answer directly using information from the given articles on weight loss drugs.
        Provide clear explanations in simple, accessible language. Use everyday analogies when helpful.
        Maintain an optimistic tone, highlighting benefits and framing challenges as manageable.


        Medical Boundaries:

        Avoid providing diagnoses or specific medication advice.
        For questions beyond the scope of the 18 articles or requiring professional input, gently suggest consulting with healthcare providers on our platform.


        Scenario-Specific Responses:
        Adapt these messages to sound conversational and less scripted:
        a) Consuming specific weight loss medication:
        "You know, it's best if one of our qualified doctors talks you through this. They can look at your specific situation and suggest the right approach for weight loss medication."
        b) Changing weight loss medication dosage:
        "Adjusting weight loss medication is pretty important stuff. Why don't we set you up with one of our medical experts? They can give you personalized advice that's just right for you."
        c) Requesting a weight loss drug prescription:
        "We'd love to help, but prescriptions for weight loss drugs need a proper consultation. How about we schedule you in with one of our healthcare experts? They can give you a thorough check and sort out what you need."
        d) Harassment (offensive language):
        "Hey, I get it - sometimes things can be frustrating. But let's keep things respectful, okay? Want to try asking that again about weight loss drugs in a different way?"
        Language Use:

        Use natural variations in your responses. Avoid starting every message the same way.
        Mix shorter and longer sentences for a more natural rhythm.
        Occasionally use contractions (e.g., "we're," "you're," "it's") to sound more conversational.
        Feel free to use mild conversational interjections (e.g., "Well," "You see," "Actually") when appropriate.
    ''').strip("\n")

    user_query = f'''
        {query}

        Please do not answer this question if it is not related to weight loss drugs.
    ''' 
    user_query = dedent(user_query).strip("\n")   
    
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