import os
import requests
from dataclasses import dataclass

@dataclass
class DeepResearchRequest:
    def __init__(self, query: str):
        self.query = query
    
    def convert_to_dict(self):
        return {
            "model": "sonar-deep-research",
            "messages": [
                {
                    "role": "user",
                    "content": self.query
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.2,
            "top_p": 0.9,
            "search_domain_filter": None,
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": "month",
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1,
            "response_format": None
        }


def initial_request(query: str):
    url = 'https://api.perplexity.ai/chat/completions'

    headers = {
        "Authorization": "Bearer " + os.getenv("PERPLEXITY_API_KEY"),
        "Content-Type": "application/json"
    }
    
    data = DeepResearchRequest(query).convert_to_dict()
    
    response = requests.post(url, headers=headers, json=data)
    
    return response.json()