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
import os
from dotenv import load_dotenv
from app.model_gateway.src import deep_research

from app.api import api_init
from app.api import api_helper
from app.response_retriever.src import response_retriever
from datetime import datetime, timedelta
import pytz
import json

from app.error_logger import (
    Error,
    Severity,
    log_error
)

# define request object structure
class querycontent(BaseModel):
    questionNo: str
    question: str
    answer: str
    followupQuestions: List[str]

class askquery(BaseModel):
    userId: str
    timestamp: str
    enable_dummy_response: bool
    specialty: str
    queries: List[querycontent]

class keep_alive_data(BaseModel):
    specialty: str 
    
class deep_research_request(BaseModel):
    query: str

# create a class for feature flags
# class feature_flags(BaseModel):
#     ans_ref: List[bool]
#     follow_up: List[bool]
#     chat_title: bool
#     cache_persistence: bool
#     model_ans_ref: str
#     model_follow_up: str

startup_variables = {
    "model_client": None,
    "products_and_specialties": None,
    "anthropic_client": None,
    "timezone": None,
    "product_specialty_map_btn_client_and_gcs": None,
    "last_cache_refresh": None,
    "global_resources": None,
    "feature_flags": None
}

load_dotenv()

# define server lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("\n", "Starting ai-chat-tes", "\n")
        
        # initialize vertex ai
        # the service account is identified on an integer basis -> 0, 1, 2 ...
        api_init.initialise_vertex_client(1)

        # initialize models
        startup_variables['model_client'] = {}      
        startup_variables['model_client']['anthropic'] = api_init.anthropic_init()
        startup_variables['model_client']['google'] = {}
        startup_variables['model_client']['google']['gemini_pro'] = api_init.initialise_gemini_pro("gemini-2.0-flash-exp")
        startup_variables['model_client']['google']['gemini_flash'] = api_init.initialise_gemini_flash()
        print("\t", "Anthropic + GCP clients initialized", "\n")
        
        # initialize timezone and last cache refresh
        startup_variables["timezone"] = "America/New_York"

        # initialize list of products and specialties under those products
        startup_variables["products_and_specialties"] = {
            "tes": ["asd", "asthma", "breast_cancer", "copd", "covid_19", "depression", "epilepsy_and_seizures", "gerd", "hemophilia", "hiv_aids", "influenza_flu", "lung_cancer", "migraine", "multiple_sclerosis", "pcos", "prostate_cancer", "psoriasis", "rheumatoid_arthritis", "sti", "t1d", "t2d", "thyroid_disorders", "tuberculosis", "wld"],
            "drugsense": ["empower_atopic_dermatitis", "empower_az_demo"],
            "rxnext_basic": ["fda_ppt_1"]
        }

        # initialize global resources
        startup_variables["global_resources"] = api_init.get_global_resources(startup_variables["products_and_specialties"])

        # product specialty map
        startup_variables["product_specialty_map_btn_client_and_gcs"] = {
            # Front end Client: GCP and code
            # {
            #     "tes":{
            #         "weight-loss-drugs": ["wld", "weight-loss-drugs"],
            #     },
            #     "drugsense": {
            #         "asthma-drugsense": ["drugsense", "empower_az_demo"],
            #         "atopic-dermatitis-drugsense": ["drugsense", "empower_atopic_dermatitis"]
            #     }
            # }
            "asd": ["tes", "asd"],
            "asthma": ["tes", "asthma"],
            "breast-cancer": ["tes", "breast_cancer"],
            "copd": ["tes", "copd"],
            "covid-19": ["tes", "covid_19"],
            "depression": ["tes", "depression"],
            "epilepsy-and-seizures": ["tes", "epilepsy_and_seizures"],
            "gerd": ["tes", "gerd"],
            "hemophilia": ["tes", "hemophilia"],
            "hiv": ["tes", "hiv_aids"],
            "influenza-flu": ["tes", "influenza_flu"],
            "lung-cancer": ["tes", "lung_cancer"],
            "migraine": ["tes", "migraine"],
            "multiple-sclerosis": ["tes", "multiple_sclerosis"],
            "pcos": ["tes", "pcos"],
            "prostate-cancer": ["tes", "prostate_cancer"],
            "psoriasis": ["tes", "psoriasis"],
            "rheumatoid-arthritis": ["tes", "rheumatoid_arthritis"],
            "sti": ["tes", "sti"],
            "type-1-diabetes": ["tes", "t1d"],
            "type-2-diabetes": ["tes", "t2d"],
            "thyroid-disorders": ["tes", "thyroid_disorders"],
            "tuberculosis": ["tes", "tuberculosis"],
            "weight-loss-drugs": ["tes", "wld"],
            "asthma-drugsense": ["drugsense", "empower_az_demo"],
            "atopic-dermatitis-drugsense": ["drugsense", "empower_atopic_dermatitis"],
            "rxnext-basic": ["rxnext_basic", "fda_ppt_1"]
        }

        # feature flags map
        # all tes conditions have the same feature flags, all drugsense conditions have the same feature flags
        startup_variables["feature_flags"] = {}
        for product in startup_variables["products_and_specialties"].keys():
            startup_variables["feature_flags"][product] = {}
            for specialty in startup_variables["products_and_specialties"][product]:
                if product == "tes":
                    if specialty in ["lung_cancer", "asd", "rheumatoid_arthritis", "depression", "hiv_aids"]:
                        startup_variables["feature_flags"][product][specialty] = {
                            "ans_ref": [
                                True,
                                {
                                    "history_context": "last 2 Q+A+Q",
                                    "format": "ans+ref"
                                }
                            ],
                            "follow_up": [
                                True,
                                {
                                    "history_context": "last Q+A",
                                    "ask_a_doctor": True
                                }
                            ],
                            "chat_title": True,
                            "cache_persistence": False,
                            "model_ans_ref": {
                                "name": "claude_sonnet",
                                "tag": "claude-3-5-sonnet-latest",
                            },
                            
                        }

                    else:
                        startup_variables["feature_flags"][product][specialty] = {
                            "ans_ref": [
                                True,
                                {
                                    "history_context": "last 2 Q+A+Q",
                                    "format": "ans+ref"
                                }
                            ],
                            "follow_up": [
                                True,
                                {
                                    "history_context": "last Q+A",
                                    "ask_a_doctor": True
                                }
                            ],
                            "chat_title": True,
                            "cache_persistence": True,
                            "model_ans_ref": {
                                "name": "claude_sonnet",
                                "tag": "claude-3-7-sonnet-latest",
                            }
                        }

                elif product == "drugsense":
                    startup_variables["feature_flags"][product][specialty] = {
                        "ans_ref": [
                            True,
                            {
                                "history_context": "last 2 Q+A+Q",
                                "format": "ans"
                            }
                        ],
                        "follow_up": [
                            True,
                            {
                                "history_context": "last Q+A",
                                "ask_a_doctor": False
                            }
                        ],
                        "chat_title": True,
                        "cache_persistence": True,
                        "model_ans_ref": {
                            "name": "claude_sonnet",
                            "tag": "claude-3-5-sonnet-latest",
                        }
                    }
                
                elif product == "rxnext_basic":
                    startup_variables["feature_flags"][product][specialty] = {
                            "ans_ref": [
                                True,
                                {
                                    "history_context": "last Q",
                                    "format": "ans"
                                }
                            ],
                            "follow_up": [
                                True,
                                {
                                    "history_context": "last Q+A",
                                    "ask_a_doctor": True
                                }
                            ],
                            "chat_title": True,
                            "cache_persistence": True,
                            "model_ans_ref": {
                                "name": "claude_sonnet",
                                "tag": "claude-3-5-sonnet-latest",
                            }
                        }

        # setup last cache refresh based on the feature_flag "cache_peristence"
        startup_variables["last_cache_refresh"] = {}
        for product in startup_variables["products_and_specialties"].keys():
            startup_variables["last_cache_refresh"][product] = {}
            for specialty in startup_variables["products_and_specialties"][product]:
                # timedelta(minutes=5) is needed for the first keep-alive call.
                if startup_variables["feature_flags"][product][specialty]["cache_persistence"]:
                    startup_variables["last_cache_refresh"][product][specialty] = datetime.now(pytz.timezone(startup_variables["timezone"])) - timedelta(minutes=5)


        yield

    except Exception as e:
        print(f"Error during startup: {e}")
        log_error( Error (
                module="FastAPI_Lifespan",
                code=1001,
                description="App startup error",
                excpetion=e
        ), Severity.ERROR)

    finally:
        print("\n", "Stopping ai-chat-tes", "\n")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cache_timeout_refresh(specialty: list[str]):
    startup_variables["last_cache_refresh"][specialty[0]][specialty[1]] = datetime.now(pytz.timezone(startup_variables["timezone"]))

@app.post("/ask-query")
async def ask_query(data: askquery, request: Request):
    try:
        xapikey = request.headers.get("x-api-key")
        if xapikey == os.environ['AI_CHAT_API_KEY']:
            # print(data)
            
            all_queries = [query.question for query in data.queries]
            all_answers = [query.answer for query in data.queries]

            if data.enable_dummy_response:
                # this was done due to empower_az_demo(dummy response enabled) and empower1(dummy response switched off)'s existence
                specialty = startup_variables["product_specialty_map_btn_client_and_gcs"][data.specialty]
                return StreamingResponse(
                    api_helper.generate_dummy_response_for_testing(
                        resources_for_specialty = getattr(startup_variables["global_resources"], specialty[0])[specialty[1]],
                    )
                )

            else:
                specialty = startup_variables["product_specialty_map_btn_client_and_gcs"][data.specialty]
                print(specialty)
                if startup_variables["feature_flags"][specialty[0]][specialty[1]]["cache_persistence"]:
                    cache_timeout_refresh(specialty = specialty)
                
                return StreamingResponse(
                    api_helper.ask_query_helper(
                        all_queries = all_queries,
                        all_answers = all_answers,
                        startup_variables = startup_variables,
                        specialty = specialty
                    )
                )
            
        else:
            return "wrong api key"
    except Exception as e:
        log_error( Error (
                module="ask-query",
                code=1002,
                description="error in ask_query endpoint",
                excpetion=e
        ), Severity.ERROR)
        print(f"Error in ask_query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.post("/keep-alive") # /keep-alive
async def keep_alive(data: keep_alive_data):
    try:
        current_time = datetime.now(pytz.timezone(startup_variables["timezone"]))
        
        specialty = startup_variables["product_specialty_map_btn_client_and_gcs"][data.specialty]

        if startup_variables["feature_flags"][specialty[0]][specialty[1]]["cache_persistence"]:
            last_cache_refresh_time = startup_variables["last_cache_refresh"][specialty[0]][specialty[1]]

            if ((current_time - last_cache_refresh_time) > timedelta(minutes=4.5)):
                print(f"Last cache refresh for {specialty[1]} at: ", last_cache_refresh_time)
                cache_timeout_refresh(specialty = specialty)
                dummy_response = response_retriever.dummy_call(
                    anthropic_client = startup_variables["model_client"]["anthropic"],
                    resources_for_specialty = getattr(startup_variables["global_resources"], specialty[0])[specialty[1]],
                    feature_flags = startup_variables["feature_flags"][specialty[0]][specialty[1]]
                )
                for _ in dummy_response:
                    continue

                dummy_call_text = "Dummy call successful. Cache timeout has been reset."
            else:
                dummy_call_text = "Dummy call blocked as cache is not expired."

            response_obj = {
                "message": dummy_call_text
            }
            
        else:
            print(f"Prompt caching is disabled for {specialty[0]} -> {specialty[1]}")
            response_obj = {
                "message": "Prompt caching is disabled!"
            }
        return response_obj
    except Exception as e:
        log_error( Error (
                module="keep-alive",
                code=1003,
                description="error in keep_alive endpoint",
                excpetion=e
        ), Severity.ERROR)
        print(f"Error in keep_alive: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post('/deep-research')
async def serve_deep_research(data: deep_research_request, request: Request):
    try:
        xapikey = request.headers.get("x-api-key")
        if xapikey == os.environ['AI_CHAT_API_KEY']:

            query = data.query
            result_report = deep_research.initial_request(query = query)
            return result_report

        else:
            return "wrong api key"
    
    except Exception as e:
        log_error( Error (
                module="deep-research",
                code=1004,
                description="error in deep_research endpoint",
                excpetion=e
        ), Severity.ERROR)
        print(f"Error in deep_research: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3080)