from app.response_retriever.src import (
    ans_ref_retriever,
    followup_questions_retriever,
    chat_title_retriever,
    dummy_calls_retriever
)
from app.prompt_builder.src import prompt_builder
from app.api.api_init import specialty

def ans_ref(ans_ref_model_client, resources_for_specialty: specialty, all_queries, all_answers, feature_flags):
    feature_flags_to_be_passed = {
        "history_context": feature_flags["ans_ref"][1]["history_context"],
        "model_ans_ref": feature_flags["model_ans_ref"]
    }
    ans_ref_prompts = prompt_builder.ans_ref_prompts(
        feature_flags = feature_flags_to_be_passed,
        resources_for_specialty = resources_for_specialty,
        all_queries = all_queries,
        all_answers = all_answers
    )

    response = ans_ref_retriever.retrieve(
        ans_ref_model_client = ans_ref_model_client,
        feature_flags = feature_flags_to_be_passed,
        prompt_obj = ans_ref_prompts,
        all_queries = all_queries,
        all_answers = all_answers
    )

    return response

def followup(anthropic_client, resources_for_specialty: specialty, last_question, last_answer, feature_flags):
    followup_prompts = prompt_builder.followup_prompts(
        feature_flags = feature_flags,
        resources_for_specialty = resources_for_specialty,
        last_question = last_question, 
        last_answer = last_answer
    )

    response = followup_questions_retriever.retrieve(
        anthropic_client = anthropic_client,
        prompt_obj = followup_prompts
    )

    return response

def chat_title(anthropic_client, chat_title_resource: str, first_question):
    chat_title_prompts = prompt_builder.chat_title_prompts(
        chat_title_resource = chat_title_resource,
        first_question = first_question
    )

    response = chat_title_retriever.retrieve(
        anthropic_client = anthropic_client,
        prompt_obj = chat_title_prompts
    )

    return response

def dummy_call(anthropic_client, resources_for_specialty: specialty, feature_flags):
    dummy_call_prompts = prompt_builder.dummy_call_prompts(
        resources_for_specialty = resources_for_specialty
    )

    feature_flags_to_be_passed = feature_flags["model_ans_ref"]
    response = dummy_calls_retriever.retrieve(
        anthropic_client = anthropic_client,
        prompt_obj = dummy_call_prompts,
        feature_flags = feature_flags_to_be_passed
    )

    return response