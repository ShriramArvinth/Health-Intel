from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)

def error_type(x):
    category = x.category
    severity = x.severity
    ans = "" + "\n"

    if category == 0:
        ans += "Harm Category: Hate Speech"
    elif category == 1:
        ans += "Harm Category: Dangerous Content"
    elif category == 2:
        ans += "Harm Category: Harassment"
    elif category == 3:
        ans += "Harm Category: Sexually Explicit"
    
    ans += '\n'

    if severity == 0:
        ans += 'Severity: Negligible'
    elif severity == 1:
        ans += 'Severity: Low'
    elif severity == 2:
        ans += 'Severity: Medium'
    elif severity == 3:
        ans += 'Severity: High'
    
    return ans

def infer(prompt: str, model: GenerativeModel):
    generation_config = GenerationConfig(
        temperature=0.9,
        top_p=1.0,
        top_k=32,
        candidate_count=1,
        max_output_tokens=8192,
    )

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    contents = [
        Part.from_uri("gs://healthquill-medical-records/Google_docs_extract_data.txt", "text/plain"),
        prompt
    ]
    
    response = ""

    try:
        response = model.generate_content(
            contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True
        )
        return response
    
    except ValueError:
        ans = 'response failed due to the following reasons:'
        exception_messages = list(map(error_type, [y for y  in list(filter(lambda d: "blocked" in d, response.candidates[0].safety_ratings))]))
        for _ in exception_messages:
            ans += _ + '\n'
        return ans

    