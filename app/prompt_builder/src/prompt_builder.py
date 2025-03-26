from dataclasses import dataclass
from textwrap import dedent
from typing import Union
from app.api.api_init import (
    specialty
)

@dataclass
class GeneralPrompt():
    def __init__(self, system_prompt: str, user_query: str):
        self.system_prompt = system_prompt
        self.user_query = user_query

@dataclass
class AnswerPrompt(GeneralPrompt):
    def __init__(self, system_prompt: str, user_query: str, knowledge: str):
        super().__init__(
            system_prompt = system_prompt, 
            user_query = user_query
        )
        self.knowledge = knowledge

# another function to define the sources paths (knowledge source, system prompt, user prompt ..)

def ans_ref_prompts(all_queries: list, all_answers: list, resources_for_specialty: specialty, feature_flags: dict):

    if feature_flags["history_context"] == "last Q":
        # specialty specific prompts inside global_resources is contained in resources_for_specialty

        # book data
        knowledge = ''.join(resources_for_specialty.knowledge)

        # system
        system_prompt = ''.join(resources_for_specialty.ans_ref_system_prompt)

        # user
        user_prompt = {
            "instructions": ''.join(resources_for_specialty.ans_ref_usr_prompt),
            "user_question": dedent(f'''
                -> User's Question:
                {all_queries[-1]}
            ''').strip("\n")
        }

        response_obj = AnswerPrompt(
            system_prompt = system_prompt,
            user_query = user_prompt,
            knowledge = knowledge
        )

        return response_obj
    
    elif feature_flags["history_context"] == "last 2 Q+A+Q":
        # specialty specific prompts inside global_resources is contained in resources_for_specialty

        # book data
        knowledge = ''.join(resources_for_specialty.knowledge)

        # system
        system_prompt = ''.join(resources_for_specialty.ans_ref_system_prompt)

        # user
        user_prompt = {
            "instructions": ''.join(resources_for_specialty.ans_ref_usr_prompt),
            "user_question": dedent(f'''
                -> User's Question:
                {all_queries[-1]}
            ''').strip("\n")
        }

        response_obj = AnswerPrompt(
            system_prompt = system_prompt,
            user_query = user_prompt,
            knowledge = knowledge
        )

        return response_obj


def followup_prompts(resources_for_specialty: specialty, last_question: str, last_answer: str, feature_flags: dict):

    if feature_flags["ask_a_doctor"]:
        # specialty specific prompts inside global_resources is contained in resources_for_specialty

        # system
        system_prompt = ''.join(resources_for_specialty.follow_up_system_prompt)

        # user
        user_prompt = dedent(f'''
            last_question:
            {last_question}

            last_answer:
            {last_answer}

            FORMATTING RULES TO BE FOLLOWED:
            For Instruction 1, respond with 3 questions.
            For Instruction 2, respond with either "true" or "false"

            output in JSON format with keys: "questions" (list), "askDoctorOnline" (bool).
        ''').strip("\n")

        response_obj = GeneralPrompt(
            system_prompt = system_prompt,
            user_query = user_prompt 
        )

        return response_obj

    else:
        # specialty specific prompts inside global_resources is contained in resources_for_specialty

        # system
        system_prompt = ''.join(resources_for_specialty.follow_up_system_prompt)

        # user
        user_prompt = dedent(f'''
            last_question:
            {last_question}

            last_answer:
            {last_answer}

            FORMATTING RULES TO BE FOLLOWED:
            respond with 3 questions.

            output in JSON format with keys: "questions" (list).
        ''').strip("\n")

        response_obj = GeneralPrompt(
            system_prompt = system_prompt,
            user_query = user_prompt 
        )

        return response_obj


def chat_title_prompts(chat_title_resource: str, first_question: str):
    
    # system
    system_prompt = chat_title_resource

    # user
    user_prompt = dedent(f'''
        This is the first question the user asked in the chat:
        {first_question if (not (first_question == "")) else "empty query"}

        Respond with a concise topic for the chat.
    ''').strip("\n")

    response_obj = GeneralPrompt(
        system_prompt = system_prompt,
        user_query = user_prompt 
    )

    return response_obj

def dummy_call_prompts(resources_for_specialty: specialty):

    # specialty specific prompts inside global_resources is contained in resources_for_specialty

    # book data
    knowledge = ''.join(resources_for_specialty.knowledge)

    # system
    system_prompt = ''.join(resources_for_specialty.ans_ref_system_prompt)

    # user
    user_prompt = {
        "instructions": 'This is just a test question.',
        "user_question": dedent(f'''
            This is just a test question to check you status. Respond with "dummy" and that will signal to us that you are up and running.
            Just say "dummy". Okay? Thank You.
        ''').strip("\n")
    }

    response_obj = AnswerPrompt(
        system_prompt = system_prompt,
        user_query = user_prompt,
        knowledge = knowledge
    )

    return response_obj