import os
import requests
from dataclasses import dataclass

@dataclass
class InitialRequest:
    def __init__(self, initial_query: str):
        self.initial_query = initial_query
    
    def convert_to_dict(self):
        return {
            "initialQuery": self.initial_query
        }

@dataclass
class FollowupRequest:
    def __init__(self, initial_query: str, followup_questions: list[str], answers: list[str]):
        self.initial_query = initial_query
        self.followup_questions = followup_questions
        self.answers = answers
    
    def convert_to_dict(self):
        return {
            "initialQuery": self.initial_query,
            "followUpQuestions": self.followup_questions,
            "answers": self.answers
        }

def initial_request(query: str):
    url = 'https://deep-research-server-944564052622.us-central1.run.app/api/que'
    headers = {
        'x-api-key': os.getenv('DEEP_RESEARCH_API_KEY'),
        'Content-Type': 'application/json'
    }
    
    data = InitialRequest(query).convert_to_dict()
    
    response = requests.post(url, headers=headers, json=data)
    print(response.json())
    return response.json()['data']

def final_request(query: str, followup_obj: list[dict[str, str]]):
    url = "https://deep-research-server-944564052622.us-central1.run.app/api/flp"
    headers = {
        'x-api-key': os.getenv('DEEP_RESEARCH_API_KEY'),
        'Content-Type': 'application/json'
    }

    ques_list = []
    ans_list = []

    for _ in followup_obj:
        ques_list.append(_["question"])
        ans_list.append(_["answer"])

    data = FollowupRequest(query, ques_list, ans_list).convert_to_dict()

    response = requests.post(url, headers=headers, json=data)
    print(response.json())
    return response.json()