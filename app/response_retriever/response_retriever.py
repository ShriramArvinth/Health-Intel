from app.response_retriever import (
    ans_ref_retriever,
    followup_questions_retriever,
    chat_title_retriever,
    dummy_calls_retriever
)
from app.prompt_builder import prompt_builder
from app.api.api_init import global_resources

def ans_ref(anthropic_client, specialty: str, all_prompts: global_resources, query):
    ans_ref_prompts = prompt_builder.ans_ref_prompts(
        specialty = specialty,
        all_prompts = all_prompts,
        query = query
    )

    response = ans_ref_retriever.retrieve(
        anthropic_client = anthropic_client,
        prompt_obj = ans_ref_prompts
    )

    return response

def followup(anthropic_client, all_prompts: global_resources, last_question, last_answer):
    followup_prompts = prompt_builder.followup_prompts(
        all_prompts = all_prompts,
        last_question = last_question, 
        last_answer = last_answer
    )

    response = followup_questions_retriever.retrieve(
        anthropic_client = anthropic_client,
        prompt_obj = followup_prompts
    )

    return response

def chat_title(anthropic_client, all_prompts: global_resources, first_question):
    chat_title_prompts = prompt_builder.chat_title_prompts(
        all_prompts = all_prompts,
        first_question = first_question
    )

    response = chat_title_retriever.retrieve(
        anthropic_client = anthropic_client,
        prompt_obj = chat_title_prompts
    )

    return response

def dummy_call(anthropic_client, all_prompts: global_resources, specialty: str):
    dummy_call_prompts = prompt_builder.dummy_call_prompts(
        all_prompts = all_prompts,
        specialty = specialty
    )

    response = dummy_calls_retriever.retrieve(
        anthropic_client = anthropic_client,
        prompt_obj = dummy_call_prompts
    )

    return response