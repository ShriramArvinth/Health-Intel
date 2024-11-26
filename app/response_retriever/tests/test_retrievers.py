import sys
from pathlib import Path
sys.path[0] = str(Path(__file__).parent.parent.parent.parent)

import unittest
from anthropic import Anthropic
from app.api.api_init import (
    global_resources,
    specialty
)
from app.response_retriever.src.response_retriever import (
    ans_ref,
    followup,
    chat_title,
    dummy_call
)

class TestRetrievers(unittest.TestCase):
    def setUp(self) -> None:
        with open("../../secrets/anthropic_key.txt", "r") as f:
            api_key = f.readline().strip()
        self.client = Anthropic(api_key = api_key)

        # set up global prompt resources
        self.all_prompts = global_resources()
        self.all_prompts.chat_title = "sample test prompt"
        self.all_prompts.follow_up = "sample test prompt"
        self.all_prompts.wld = specialty()
        self.all_prompts.wld.ans_ref_system_prompt = "sample test prompt"
        self.all_prompts.wld.ans_ref_usr_prompt = "sample test prompt"
        self.all_prompts.wld.knowledge = "some sample test data"
        self.all_prompts.wld.pre_def_response = "some sample predefined response"

        # set up specific inputs for each retriever as per the flow
        self.specialty = "wld"
        self.user_query = "sample user query"
        self.last_question = "this is a sample last question"
        self.last_answer = "this was a sample last answer"
        self.first_question = "sample first question"
    
    def tearDown(self) -> None:
        del self.all_prompts, self.user_query, self.last_question, self.last_answer, self.first_question, self.specialty

    def test_ans_ref(self):
        """Test answer + refrences retriever"""
        response = "".join(
            ans_ref(
                anthropic_client = self.client,
                all_prompts = self.all_prompts,
                query = self.user_query,
                specialty = self.specialty
            )
        )
        self.assertIsInstance(response, str)
    
    def test_followup(self):
        """Test followup retriever"""
        response = followup(
            all_prompts = self.all_prompts,
            anthropic_client = self.client,
            last_question = self.last_question,
            last_answer = self.last_answer
        )
        self.assertIsInstance(response, str)
    
    def test_chat_title(self):
        """Test chat title retriever"""
        response = chat_title(
            all_prompts = self.all_prompts,
            anthropic_client = self.client,
            first_question = self.first_question
        )
        self.assertIsInstance(response, str)
    
    def test_dummy_call(self):
        """Test dummy call retriever"""
        response = "".join(
            dummy_call(
                anthropic_client = self.client,
                all_prompts = self.all_prompts,
                specialty = self.specialty
            )
        )
        self.assertIsInstance(response, str)

if __name__ == "__main__":
    unittest.main(verbosity=2)