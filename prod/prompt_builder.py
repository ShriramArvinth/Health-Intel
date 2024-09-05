from typing import List
import json

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

Answer the user's current query by taking into context the past queries and the articles. 
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