def infer(client, prompt):
    response = client.beta.prompt_caching.messages.create(
        model = "claude-3-5-haiku-latest",
        max_tokens = 1024,
        system = prompt["system"],
        messages = prompt["messages"],
        stream = False
    )
    
    return response.content[0].text