from vertexai.generative_models._generative_models import (Content, GenerationConfig)
from vertexai.preview.generative_models import GenerativeModel

def infer_gemini(client: GenerativeModel, contents: list[Content]):

    parameters = GenerationConfig(
        temperature = 0.9,
        top_p = 0.9,
        top_k = 40,
        candidate_count = 1, #number of response variations to return
        max_output_tokens = 8192,
        stop_sequences = ["STOP!"], #terminate the response once the model encounters this string in its own response
    )

    response = client.generate_content(
        contents=contents,
        generation_config = parameters,
        stream=True
    )

    for chunk in response:
        yield chunk.text