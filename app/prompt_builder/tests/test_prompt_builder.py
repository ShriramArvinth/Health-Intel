import sys
from pathlib import Path
sys.path[0] = str(Path(__file__).parent.parent.parent.parent)

import unittest
from app.api.api_init import (
    global_resources,
    specialty
)

from app.prompt_builder.src.prompt_builder import (
    ans_ref_prompts,
    followup_prompts,
    chat_title_prompts,
    dummy_call_prompts,
    GeneralPrompt,
    AnswerPrompt
)

class TestPromptBuilders(unittest.TestCase):
    def setUp(self) -> None:
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
    
    def test_ans_ref_prompts(self):
        """Test answer + refrences prompt builder"""
        prompt = ans_ref_prompts(
            query = self.user_query,
            all_prompts = self.all_prompts,
            specialty = self.specialty
        )
        self.assertIsInstance(prompt, AnswerPrompt)

    def test_followup_prompts(self):
        """Test followup prompt builder"""
        prompt = followup_prompts(
            all_prompts = self.all_prompts,
            last_question = self.last_question,
            last_answer = self.last_answer
        )
        self.assertIsInstance(prompt, GeneralPrompt)

    def test_chat_title_prompts(self):
        """Test chat title prompt builder"""
        prompt = chat_title_prompts(
            all_prompts = self.all_prompts,
            first_question = self.first_question,
        )
        self.assertIsInstance(prompt, GeneralPrompt)

    def test_dummy_call_prompts(self):
        """Test dummy call prompt builder"""
        prompt = dummy_call_prompts(
            all_prompts = self.all_prompts,
            specialty = self.specialty
        )
        self.assertIsInstance(prompt, AnswerPrompt)

if __name__ == "__main__":
    unittest.main(verbosity=2)