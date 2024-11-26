from app.model_gateway.src import claude_haiku
from app.prompt_builder.src.prompt_builder import (
    GeneralPrompt
)

def retrieve(anthropic_client, prompt_obj: GeneralPrompt):
    prompt = {
        "system": [
            {
                "type": "text",
                "text": prompt_obj.system_prompt + "\n",
                "cache_control": {"type": "ephemeral"}
            }
        ],
        "messages": [
            {
            "role": "user",
            "content": prompt_obj.user_query
            }
        ],
    }

    response = claude_haiku.infer(
        client = anthropic_client,
        prompt = prompt
    )

    return response