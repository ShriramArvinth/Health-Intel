from anthropic import Anthropic

def infer(client: Anthropic, prompt, tag: str):
    response = client.messages.create(
        model = tag,
        max_tokens = 1024,
        system = prompt["system"],
        messages = prompt["messages"],
        stream = True
    )
    for event in response:
        if event.type == "content_block_delta":
            yield(event.delta.text)
