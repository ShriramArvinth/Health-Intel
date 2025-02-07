from app.model_gateway.src import claude_sonnet
from app.prompt_builder.src.prompt_builder import (
    AnswerPrompt
)

def retrieve(anthropic_client, prompt_obj: AnswerPrompt, feature_flags: dict, all_queries: list, all_answers: list):
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
                            "cache_control": {"type": "ephemeral"}
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

        response = claude_sonnet.infer(
            client = anthropic_client,
            prompt = prompt
        )

        return response
    
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
                            "cache_control": {"type": "ephemeral"}
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
                            "cache_control": {"type": "ephemeral"}
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
            client = anthropic_client,
            prompt = prompt
        )

        return response