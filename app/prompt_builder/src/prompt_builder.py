from dataclasses import dataclass
from textwrap import dedent
from app.api.api_init import (
    global_resources,
    specialty as spc
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

def ans_ref_prompts(query: str, specialty: str, all_prompts: global_resources):

    # specialty specific prompts inside global_resources
    specialty_obj: spc = getattr(all_prompts, specialty)

    # book data
    knowledge = ''.join(specialty_obj.knowledge)

    # system
    system_prompt = ''.join(specialty_obj.ans_ref_system_prompt)

    # user
    user_prompt = {
        "instructions": ''.join(specialty_obj.ans_ref_usr_prompt),
        "user_question": dedent(f'''
            -> User's Question:
            {query}
        ''').strip("\n")
    }

    response_obj = AnswerPrompt(
        system_prompt = system_prompt,
        user_query = user_prompt,
        knowledge = knowledge
    )

    return response_obj

def followup_prompts(specialty: str, all_prompts: global_resources, last_question: str, last_answer: str ):

    # specialty specific prompts inside global_resources
    specialty_obj: spc = getattr(all_prompts, specialty)

    # system
    system_prompt = ''.join(specialty_obj.follow_up_system_prompt)

    # user
    user_prompt = dedent(f'''
        This is the last question the user has asked:
        {last_question}

        This is the answer provided for that question:
        {last_answer}

        Respond with only 3 questions
        Output in JSON format with keys: "questions" (list).
    ''').strip("\n")

    response_obj = GeneralPrompt(
        system_prompt = system_prompt,
        user_query = user_prompt 
    )

    return response_obj

def chat_title_prompts(all_prompts: global_resources, first_question: str):
    
    # system
    system_prompt = ''.join(all_prompts.chat_title)

    # user
    user_prompt = dedent(f'''
        This is the first question the user asked in the chat:
        {first_question}

        Respond with a concise topic for the chat.
    ''').strip("\n")

    response_obj = GeneralPrompt(
        system_prompt = system_prompt,
        user_query = user_prompt 
    )


    return response_obj

def dummy_call_prompts(all_prompts: global_resources, specialty: str):

    # specialty specific prompts inside global_resources
    specialty_obj: spc = getattr(all_prompts, specialty)

    # book data
    knowledge = ''.join(specialty_obj.knowledge)

    # system
    system_prompt = ''.join(specialty_obj.ans_ref_system_prompt)

    # user
    user_prompt = {
        "instructions": ''.join(specialty_obj.ans_ref_usr_prompt),
        "user_question": dedent(f'''
            This is just a test question. 
            DO NOT FOLLOW THE RESPONSE FORMAT.
            Just respond with "dummy" and nothing else.
        ''').strip("\n")
    }

    response_obj = AnswerPrompt(
        system_prompt = system_prompt,
        user_query = user_prompt,
        knowledge = knowledge
    )

    return response_obj