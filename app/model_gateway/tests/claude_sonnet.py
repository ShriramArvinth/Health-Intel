def infer(client, prompt):
    response = client.beta.prompt_caching.messages.create(
        model = "claude-3-5-sonnet-latest",
        max_tokens = 1024,
        system = prompt["system"],
        messages = prompt["messages"],
        stream = True
    )
    for event in response:
        if event.type == "content_block_delta":
            yield(event.delta.text)
