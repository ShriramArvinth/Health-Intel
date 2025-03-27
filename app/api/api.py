# define top folder structure for absolute imports
from api_init import init_import_structure
init_import_structure()

# fastapi imports
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import uuid
import threading

from app.api import (
    api_init, 
    api_helper,
    custom_threads
)
from app.response_retriever.src import response_retriever
from datetime import datetime, timedelta
import pytz

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
    query_id: str

startup_variables = {
    "model_client": None,
    "products_and_specialties": None,
    "anthropic_client": None,
    "timezone": None,
    "product_specialty_map_btn_client_and_gcs": None,
    "specialty_keep_alive_threads": None,
    "thread_lock": None,
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
                    if specialty in ["asd", "depression", "hiv_aids"]:
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
                    elif specialty in ["lung_cancer", "rheumatoid_arthritis"]: 
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
                                "name": "gemini_pro",
                                "tag": "gemini-2.0-flash-exp",
                                "service_acc": 0
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

        # setup keep alive threads for each product and specialty
        startup_variables["specialty_keep_alive_threads"] = {}
        for product in startup_variables["products_and_specialties"].keys():
            startup_variables["specialty_keep_alive_threads"][product] = {}
            for specialty in startup_variables["products_and_specialties"][product]:
                if startup_variables["feature_flags"][product][specialty]["cache_persistence"]:
                    startup_variables["specialty_keep_alive_threads"][product][specialty] = {}
                    startup_variables["specialty_keep_alive_threads"][product][specialty]["thread"] = None

                    # lock for each specialty's thread set in startup variables keep alive threads to access the lock and update
                    startup_variables["specialty_keep_alive_threads"][product][specialty]["thread_lock"] = threading.Lock()

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
        for product_threads in startup_variables["specialty_keep_alive_threads"].values():
            for specialty_thread in product_threads.values():
                with specialty_thread.get("thread_lock"):
                    thread = specialty_thread.get("thread")
                    if thread and thread.is_alive():
                        if not thread.is_stopped():
                            thread.stop()
                        thread.join()
        print("\n", "Stopping ai-chat-tes", "\n")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
                    specialty_thread_lock = startup_variables["specialty_keep_alive_threads"][specialty[0]][specialty[1]]["thread_lock"]
                    with specialty_thread_lock:
                        existing_thread: custom_threads.StoppableThread = startup_variables["specialty_keep_alive_threads"][specialty[0]][specialty[1]]["thread"]
                        
                        if existing_thread is None or not existing_thread.is_alive():
                            print(f"Starting keep-alive thread for {specialty[0]} -> {specialty[1]}")

                        else:
                            if not existing_thread.is_stopped():
                                existing_thread.stop()

                        new_thread = custom_threads.StoppableThread(
                            target=api_helper.keep_alive_thread_runner,
                            args=(12, 270),  # Positional arguments: break_even, interval
                            kwargs={
                                "anthropic_client": startup_variables["model_client"]["anthropic"],
                                "resources_for_specialty": getattr(startup_variables["global_resources"], specialty[0])[specialty[1]],
                                "feature_flags": startup_variables["feature_flags"][specialty[0]][specialty[1]]
                            }
                        )
                        startup_variables["specialty_keep_alive_threads"][specialty[0]][specialty[1]]["thread"] = new_thread
                        new_thread.start()
                    
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
    
@app.post('/deep-research', status_code=status.HTTP_200_OK)
async def serve_deep_research(data: deep_research_request, request: Request, background_tasks: BackgroundTasks, response: Response):
    try:
        xapikey = request.headers.get("x-api-key")
        if xapikey == os.environ['AI_CHAT_API_KEY']:
            if data.query_id == "":
                query = data.query
                query_id = str(uuid.uuid4())
                background_tasks.add_task(api_helper.deepresearch_job, query, query_id)
                response.status_code = status.HTTP_201_CREATED
                return {
                    "status": "processing",
                    "query_id": query_id,
                    "message": "Deep research job has been initiated"
                }

            else:
                result_report = api_helper.check_and_pull_deepresearch_results(data.query_id)
                if result_report:
                    result_report["status"] = "completed"
                    return result_report
                else:
                    response.status_code = status.HTTP_202_ACCEPTED
                    return {
                        "status": "processing",
                        "query_id": data.query_id,
                        "message": "Deep research job is still processing"
                    }

        else:
            response.status_code = status.HTTP_401_UNAUTHORIZED
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