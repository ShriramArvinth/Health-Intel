from vertexai_init import (
    vertexai_init as init_vertex,
    model_configuration as init_model
)
from prompt_builder import build_prompt
from infer import infer
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
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

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask-query")
async def ask_query(data: askquery, request: Request):
    # // check the request.headers["x-api-key"] , make sure the value is = 
    xapikey = request.headers.get("x-api-key")
    if (xapikey == 'Cp)L9dt)ACeZIAv(RDYX)V8NPx+dEFMh(eGFDd(sAxQvEMdZh4y(svKC(4mWCj'):
        # print(data)
        prompt = build_prompt([query.question for query in data.queries])
        # with open("full_prompt.txt", "w") as f:
        #     f.write(prompt)
        response = infer(prompt = prompt, model = model)
        # print(response.text)
        cleaned_response = response.text.replace("*", "")
        json_parsed = json.loads(str(cleaned_response))
        # print(json_parsed)

        send_data = data
        send_data.queries[-1].answer = json_parsed['answer']
        send_data.queries[-1].followupQuestions = json_parsed['followup-questions']
        # print(send_data)
        return send_data
    else:
        return "wrong api key"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3090)