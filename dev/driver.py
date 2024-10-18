from vertexai_init import (
    vertexai_init as init_vertex,
    model_configuration as init_model,
    flash_model_configuration as init_flash_model,
    anthropic_init as init_anthropic
)
from prompt_builder import (
    build_prompt,
    build_prompt_flash,
    build_prompt_sonnet,
    build_prompt_haiku
)
from infer import (
    infer,
    infer_flash,
    infer_sonnet,
    infer_haiku
)
from contextlib import asynccontextmanager
from dummy_calls import run_dummy_calls
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from threading import Thread, Event
import json

class querycontent(BaseModel):
    questionNo: str
    question: str
    answer: str
    followupQuestions: List[str]

class askquery(BaseModel):
    userId: str
    timestamp: str
    queries: List[querycontent]

# init_vertex()
# model = init_model()
# flash_model = init_flash_model()
anthropic_client = init_anthropic()

stop_event = Event()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will run during startup
    print("Starting dummy calls Thread")
    dummy_calls_thread = Thread(
        target=run_dummy_calls,
        args=(
            anthropic_client,  # Pass the client
            "09:00",           # Start time
            "23:59",           # End time
            4.5,               # Interval in minutes
            'America/New_York',  # Timezone
            stop_event
        )
    )
    dummy_calls_thread.start()
    try:
        yield
    finally:
        # This will run during application shutdown
        stop_event.set()  # Signal the thread to stop
        dummy_calls_thread.join()  # Wait for the thread to finish

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def content_generator(all_queries: List[str]):
    prompt = build_prompt_sonnet(
       query=all_queries[-1]
    )
    responses = infer_sonnet(prompt=prompt, client=anthropic_client)
    
    # Initialize an empty string to store all responses
    all_responses_text = ""

    for response in responses:
        # Concatenate the current response text to the all_responses_text variable
        all_responses_text += response.text + "\n"  # Add a newline for separation
        yield response.text

    # Print the concatenated responses after yielding all individual responses
   # print("All Responses:\n", all_responses_text)
    
    yield "$end_of_answer_stream$"

    haiku_prompt = build_prompt_haiku(all_queries[int((len(all_queries) - 1))], all_responses_text)
    followup_questions = infer_haiku(prompt=haiku_prompt, client=anthropic_client)
    # Yield follow-up questions if needed
    yield followup_questions.text
    yield "\n $end_of_followup$ \n"

@app.post("/ask-query")
async def ask_query(data: askquery, request: Request):
    # Make sure x-api-key's value is equal to the one we have
    xapikey = request.headers.get("x-api-key")
    if (xapikey == 'Cp)L9dt)ACeZIAv(RDYX)V8NPx+dEFMh(eGFDd(sAxQvEMdZh4y(svKC(4mWCj'):
        # Print the list of queries
        all_queries = [query.question for query in data.queries]
        print("Last Question:", all_queries[int((len(all_queries) - 1))])  # Add this line to print the queries
        return StreamingResponse(content_generator(all_queries=all_queries))
    else:
        return "wrong api key"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3080)
