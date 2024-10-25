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
    build_prompt_haiku_followup,
    build_prompt_haiku_chat_title
)
from infer import (
    infer,
    infer_flash,
    infer_sonnet,
    infer_haiku
)
from api_helper import parse_streaming_response
from contextlib import asynccontextmanager
from dummy_calls import (run_dummy_calls, make_dummy_call)
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from threading import Thread, Event
from datetime import datetime, timedelta
import re
import pytz
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

class dummydata(BaseModel):
    data: str 

# init_vertex()
# model = init_model()
# flash_model = init_flash_model()
anthropic_client = init_anthropic()

# dummy calls
timezone: str = "America/New_York"

    # dummy calls handled from client -- initialise last dummy call at server_start to -5mins(curr_time) to make dummy_calls immediately
last_dummy_call = datetime.now(pytz.timezone(timezone)) - timedelta(minutes=5)

    # dummy calls handled automatically by the server
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
            timezone,
            stop_event
        )
    )
    dummy_calls_thread.start()
    try:
        yield
    finally:
        # This will run during application shutdown
        stop_event.set()  # Signal the thread to stop
        dummy_calls_thread.join()     # Wait for the thread to finish


# start app
app = FastAPI(lifespan=lifespan) # spawn run_dummy_calls thread as soon as the server starts up
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def content_generator(all_queries: List[str]):
    prompt = build_prompt_sonnet(
       query = all_queries[-1]
    )

    # responses = infer(prompt = prompt, model = model)
    response = infer_sonnet(prompt = prompt, client = anthropic_client)
    parsed_stream = parse_streaming_response(response = response)

    answer_to_query = ""
    chunk_flag = True
    for chunk in parsed_stream:
        if "$relevant_articles_begin$" in chunk:
            chunk_flag = not(chunk_flag)
        elif "$relevant_articles_end$" in chunk:
            chunk_flag = not(chunk_flag)
        if chunk_flag:
            answer_to_query += re.sub(r'\$.*?\$', '', chunk)
        # print(chunk, end = "")
        # print('\n')
        yield chunk

    yield "$end_of_answer_stream$"

    haiku_prompt = build_prompt_haiku_followup(all_queries[-1], answer_to_query)
    followup_questions = infer_haiku(prompt = haiku_prompt, client = anthropic_client)
    yield followup_questions

    # return chat title, if its the first question in the chat window
    if(len(all_queries) == 1):
        yield "$end_of_followup_stream$"
        haiku_prompt = build_prompt_haiku_chat_title(first_question = all_queries[0])
        chat_title = infer_haiku(prompt = haiku_prompt, client = anthropic_client)
        yield chat_title


@app.post("/ask-query")
async def ask_query(data: askquery, request: Request):
    # Validate x-api-key's value
    xapikey = request.headers.get("x-api-key")
    if (xapikey == 'Cp)L9dt)ACeZIAv(RDYX)V8NPx+dEFMh(eGFDd(sAxQvEMdZh4y(svKC(4mWCj'):
        # print(data)
        all_queries = [query.question for query in data.queries]
        return StreamingResponse(content_generator(all_queries = all_queries))
    else:
        return "wrong api key"


@app.post("/dummy-call")
async def dummy_call(data: dummydata):
    current_time = datetime.now(pytz.timezone(timezone))
    global last_dummy_call # refer to the global variable within this function
    
    dummy_response_text = ""
    if ((current_time - last_dummy_call) > timedelta(minutes=4.5)):
        print(last_dummy_call)
        dummy_response = make_dummy_call(client=anthropic_client)
        for _ in dummy_response:
            dummy_response_text += _
        last_dummy_call = current_time
    else:
        dummy_response_text = "dummy call blocked"
    # return StreamingResponse((x for x in dummy_response_text))

    response_obj = {
        "message": dummy_response_text
    }
    return response_obj

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3080)