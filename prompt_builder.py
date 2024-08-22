from typing import List
import json

def get_articles():
    with open("articles.json", mode="r", encoding="utf-8") as read_file:
        json_data = json.load(read_file)
        return json_data

def line_by_line(queries: List[str]):
    print(queries)
    data = ''
    for _ in queries:
        data += _
        data += '\n'
        print('line by line', data)
    return data

def build_prompt(user_queries: List[str]):
    # print(user_queries)
    prompt = f"""

Below are all the articles realted to weight loss expressed in JSON format that includes title, sub-title and article content:
{get_articles()}

These are the questions the user has previously asked:
{line_by_line(user_queries[:-1]) if(len(user_queries) > 1) else '<<The user has started a new chat, hence there is no query history>>'}

This is the user's current query:
{user_queries[-1]}

Answer the user's current query by taking into context the past queries and the articles. 

"""
    return prompt