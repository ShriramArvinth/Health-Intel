from anthropic import Anthropic

def infer(client: Anthropic, prompt):
    response = client.messages.create(
        model = "claude-3-5-haiku-latest",
        max_tokens = 1024,
        system = prompt["system"],
        messages = prompt["messages"],
        stream = False
    )
    
    return response.content[0].text