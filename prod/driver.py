from vertexai_init import (
    vertexai_init as init_vertex,
    model_configuration as init_model,
    flash_model_configuration as init_flash_model
)
from prompt_builder import (
    build_prompt,
    build_prompt_flash
)
from infer import (
    infer,
    infer_flash
)
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json

class querycontent(BaseModel):
    questionNo: str
    question: str
    answer:str
    followupQuestions: List[str]

class askquery(BaseModel):
    userId: str
    timestamp: str
    queries: List[querycontent]

init_vertex()
model = init_model()
flash_model = init_flash_model()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def content_generator(all_queries: List[str]):
    prompt = build_prompt(all_queries[-1])
    responses = infer(prompt = prompt, model = model)
    for response in responses:
        # print(response.text)
        # print('\n')
        yield response.text

    yield "$end_of_answer_stream$"

    flash_prompt = build_prompt_flash(all_queries)
    followup_questions = infer_flash(prompt=flash_prompt, model=flash_model)
    yield followup_questions.text



@app.post("/ask-query")
async def ask_query(data: askquery, request: Request):
    # // check the request.headers["x-api-key"] , make sure the value is = 
    xapikey = request.headers.get("x-api-key")
    if (xapikey == 'Cp)L9dt)ACeZIAv(RDYX)V8NPx+dEFMh(eGFDd(sAxQvEMdZh4y(svKC(4mWCj'):
        # print(data)
        all_queries = [query.question for query in data.queries]
        return StreamingResponse(content_generator(all_queries = all_queries))
    else:
        return "wrong api key"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3080)