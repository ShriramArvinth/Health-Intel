# define top folder structure for absolute imports
from api_init import init_import_structure
init_import_structure()

# fastapi imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager

from app.api import api_init
from app.api import api_helper
from app.response_retriever import response_retriever
from datetime import datetime, timedelta
import pytz

# define request object structure
class querycontent(BaseModel):
    questionNo: str
    question: str
    answer:str
    followupQuestions: List[str]

class askquery(BaseModel):
    userId: str
    timestamp: str
    enable_dummy_response: bool
    specialty: str
    queries: List[querycontent]

class keep_alive_data(BaseModel):
    data: str 

startup_variables = {
    "anthropic_client": None,
    "timezone": None,
    "last_cache_refresh": None,
    "global_resources": None
}

# define server lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n", "Starting ai-chat-tes", "\n")
    
    # initialize anthropic
    startup_variables['anthropic_client'] = api_init.anthropic_init()
    print("\t", "Anthropic client initialized", "\n")
    
    # initialize timezone and last cache refresh
    startup_variables["timezone"] = "America/New_York"
    startup_variables["last_cache_refresh"] = datetime.now(pytz.timezone(startup_variables["timezone"])) - timedelta(minutes=5)

    # initialize global resources
    startup_variables["global_resources"] = api_init.get_global_resources()

    yield

    print("\n", "Stopping ai-chat-tes", "\n")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cache_timeout_refresh():
    startup_variables["last_cache_refresh"] = datetime.now(pytz.timezone(startup_variables["timezone"]))

@app.post("/ask-query")
async def ask_query(data: askquery, request: Request):   
    
    xapikey = request.headers.get("x-api-key")
    if (xapikey == 'Cp)L9dt)ACeZIAv(RDYX)V8NPx+dEFMh(eGFDd(sAxQvEMdZh4y(svKC(4mWCj'):
        # print(data)

        if data.specialty == "weight-loss-drugs":
            specialty = "wld"

        if (data.enable_dummy_response):
            return StreamingResponse(
                api_helper.generate_dummy_response_for_testing(
                    all_prompts = startup_variables["global_resources"],
                    specialty = specialty
                )
            )

        else:
            all_queries = [query.question for query in data.queries]
            cache_timeout_refresh()
            
            return StreamingResponse(
                api_helper.ask_query_helper(
                    all_queries = all_queries,
                    startup_variables = startup_variables,
                    specialty = specialty
                )
            )
        
    else:
        return "wrong api key"

@app.post("/dummy-calls") # /keep-alive
async def keep_alive(data: keep_alive_data):
    current_time = datetime.now(pytz.timezone(startup_variables["timezone"]))
    last_cache_refresh = startup_variables["last_cache_refresh"]

    dummy_call_text = ""
    if ((current_time - last_cache_refresh) > timedelta(minutes=4.5)):
        print("Last cache refresh at: ", last_cache_refresh)
        cache_timeout_refresh()
        dummy_response = response_retriever.dummy_call(anthropic_client = startup_variables["anthropic_client"])
        for _ in dummy_response:
            dummy_call_text += _
    else:
        dummy_call_text = "dummy call blocked"

    response_obj = {
        "message": dummy_call_text
    }
    return response_obj

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3080)