from vertexai.generative_models._generative_models import (Content, Part, GenerationConfig)
from vertexai.preview.generative_models import GenerativeModel

def infer_gemini(generative_multimodal_model: GenerativeModel, prompt: str):

    parameters = GenerationConfig(
        temperature = 0.9,
        top_p = 0.9,
        top_k = 40,
        candidate_count = 1, #number of response variations to return
        max_output_tokens = 8192,
        stop_sequences = ["STOP!"], #terminate the response once the model encounters this string in its own response
    )

    response = generative_multimodal_model.generate_content(
        contents=[
            Content(role="user", parts=[Part.from_text(prompt)]),
        ],
        generation_config = parameters,
        stream=False
    )

    return response.text