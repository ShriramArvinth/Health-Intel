from app.model_gateway.src import claude_sonnet
from app.model_gateway.src import gemini_pro
from vertexai.generative_models._generative_models import (Content, Part)
from typing import Union
from vertexai.preview.generative_models import GenerativeModel
from anthropic import Anthropic
from app.prompt_builder.src.prompt_builder import (
    AnswerPrompt
)

def retrieve(ans_ref_model_client: Union[GenerativeModel, Anthropic], prompt_obj: AnswerPrompt, feature_flags: dict, all_queries: list, all_answers: list):

    if feature_flags["model_ans_ref"]['name'] == "claude_sonnet":
        if feature_flags["history_context"] == "last Q":
            prompt = {
                "system": [
                    {
                        "type": "text",
                        "text": prompt_obj.system_prompt + "\n",
                    },
                    {
                        "type": "text",
                        "text": "DATA: \n" + prompt_obj.knowledge,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_obj.user_query["instructions"]
                            }
                        ]
                    },
                    # we need the assistant block as a placeholder, as the anthropic API doesn't allow for messages of the same role consecutively.
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "Okay, I will follow your INSTRUCTIONS",
                                # "cache_control": {"type": "ephemeral"}
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_obj.user_query["user_question"]
                            }
                        ]
                    }
                ],
            }
        
        elif feature_flags["history_context"] == "last 2 Q+A+Q":
            prompt = {
                "system": [
                    {
                        "type": "text",
                        "text": prompt_obj.system_prompt + "\n",
                    },
                    {
                        "type": "text",
                        "text": "DATA: \n" + prompt_obj.knowledge,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_obj.user_query["instructions"]
                            }
                        ]
                    },
                    # we need the assistant block as a placeholder, as the anthropic API doesn't allow for messages of the same role consecutively.
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "Okay, I will follow your INSTRUCTIONS",
                                # "cache_control": {"type": "ephemeral"}
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": all_queries[-2]
                            }
                        ]
                    },
                    {
                        "role": "assistant",
                        "content":[
                            {
                                "type": "text",
                                "text": all_answers[-2]
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "-> User's Question:\n" + all_queries[-1]
                            }
                        ]
                    }
                ] if len(all_answers) > 1 else [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_obj.user_query["instructions"]
                            }
                        ]
                    },
                    # we need the assistant block as a placeholder, as the anthropic API doesn't allow for messages of the same role consecutively.
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "Okay, I will follow your INSTRUCTIONS",
                                # "cache_control": {"type": "ephemeral"}
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "-> User's Question:\n" + all_queries[-1]
                            }
                        ]
                    }
                ],
            }
            
        response = claude_sonnet.infer(
            client = ans_ref_model_client,
            prompt = prompt,
            tag = feature_flags["model_ans_ref"]["tag"]
        )

        return response
    
    elif feature_flags["model_ans_ref"]["name"] == "gemini_pro":
        ans_ref_model_client._system_instruction = [
            prompt_obj.system_prompt,
            "DATA: " + prompt_obj.knowledge,
        ]

        if feature_flags["history_context"] == "last Q" or len(all_answers) == 1:
            prompt = [
                Content(
                    role="user",
                    parts=[Part.from_text(prompt_obj.user_query["instructions"])]
                ), 
                Content(
                    role="model",
                    parts=[Part.from_text("Okay, I will follow your INSTRUCTIONS")]
                ),
                Content(
                    role="user",
                    parts=[Part.from_text(prompt_obj.user_query["user_question"])]
                )
            ]
        elif feature_flags["history_context"] == "last 2 Q+A+Q" and len(all_answers) > 1:
            prompt = [
                Content(
                    role="user",
                    parts=[Part.from_text(prompt_obj.user_query["instructions"])]
                ), 
                Content(
                    role="model",
                    parts=[Part.from_text("Okay, I will follow your INSTRUCTIONS")]
                ),
                Content(
                    role="user",
                    parts=[Part.from_text(all_queries[-2])]
                ),
                Content(
                    role="model",
                    parts=[Part.from_text(all_answers[-2])]
                ),
                Content(
                    role="user",
                    parts=[Part.from_text(prompt_obj.user_query["user_question"])]
                )
            ]

        response = gemini_pro.infer_gemini(
            client = ans_ref_model_client,
            contents = prompt
        )

        return response
        