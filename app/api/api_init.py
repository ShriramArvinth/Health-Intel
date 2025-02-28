from dataclasses import dataclass
from anthropic import Anthropic
from pathlib import Path
import sys
from google.cloud.storage import Client, transfer_manager
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from google.oauth2 import service_account
import os
import json
import shutil

# type definitions
@dataclass
class specialty():
    def __init__(self):
        self.ans_ref_system_prompt: str
        self.ans_ref_usr_prompt: str
        self.follow_up_system_prompt: str
        self.knowledge: str
        self.pre_def_response: dict

@dataclass
class global_resources():
    def __init__(self):
        self.chat_title: str
        self.drugsense: dict[str, specialty]
        self.tes: dict[str, specialty]
        self.rxnext_basic: dict[str, specialty]
        # self.wld: specialty
        # self.t1d: specialty

    def __init__(self):
        self.chat_title = ""
        self.drugsense = {}
        self.tes = {}
        self.rxnext_basic = {}

def init_import_structure():
    sys.path[0] = str(Path(__file__).parent.parent.parent)

def anthropic_creds():
    try:
        with open("../secrets/anthropic_key.txt", "r") as f:
            api_key = f.readline().strip()
            if not api_key:
                raise ValueError("API key file is empty.")
        return api_key
    except FileNotFoundError:
        print("API key file not found.")
        return None

def anthropic_init():
    client = Anthropic(
        api_key=anthropic_creds(),
    )

    return client

def initialise_vertex_client(service_acc: int) -> bool:

    # /app/api/
    current_dir = os.getcwd()
    service_account_file_path = os.path.join(current_dir, "../secrets/service_account" + (str(service_acc) if service_acc else "") + ".json")

    with open(service_account_file_path, 'r') as f:
        service_account_info = json.load(f)
        project_id = service_account_info.get("project_id")
        
    vertexai.init(
        project=project_id, 
        location="us-central1", 
        credentials=service_account.Credentials.from_service_account_file(filename = service_account_file_path)
    )
    return True

def initialise_gemini_pro(tag: str) -> GenerativeModel:
    generative_multimodal_model = GenerativeModel(
        model_name=tag,
        # system_instruction=[
        #     "Your name is Tes. You represent a healthcare platform who always responds to our user's questions in a polite yet professional and jovial tone."
        # ]
    )
    return generative_multimodal_model

def initialise_gemini_flash() -> GenerativeModel:
    generative_multimodal_model = GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        # system_instruction=[
        #     "Your name is Tes. You represent a healthcare platform who always responds to our user's questions in a polite yet professional and jovial tone."
        # ]
    )
    return generative_multimodal_model

def load_text_file(filepath):
    with open(filepath, 'r') as file:
        return file.read().strip()

def get_gcp_resources():

    # /app/api/
    current_dir = os.getcwd()
    service_account_file = os.path.join(current_dir, "../secrets/service_account.json")
    creds = service_account.Credentials.from_service_account_file(filename = service_account_file)

    storage_client = Client(
        credentials=creds
    )

    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket
    bucket_name = os.getenv("STORAGE_BUCKET_NAME")

    # The ID of your GCS object
    max_results=1000

    # The path to which the file should be downloaded
    destination_directory = os.path.join(current_dir, "../gcp_download/")

    workers = 8

    bucket = storage_client.bucket(bucket_name)
    blob_names = [blob.name for blob in bucket.list_blobs(max_results=max_results)]

    results = transfer_manager.download_many_to_path(
        bucket, blob_names, destination_directory=destination_directory, max_workers=workers
    )

    for name, result in zip(blob_names, results):
        # The results list is either `None` or an exception for each blob in
        # the input list, in order.

        if isinstance(result, Exception):
            print("created {} due to: {}".format(name, result))
        else:
            print("Downloaded {} to {}.".format(name, destination_directory + name))

    return destination_directory

def get_global_resources(products_and_specialties: dict[str, list[str]]):
    try:
        from app.error_logger import (
            Error,
            Severity,
            log_error
        )
        resources_directory = get_gcp_resources()
        # name of the global resources object
        resources = global_resources()

        # Load chat_title and follow_up
        resources.chat_title = load_text_file(os.path.join(resources_directory, 'chat_title.txt'))

        # Loop through each specialty to load data
        for product in products_and_specialties.keys():

            # handle case where the directory doesn't exist because of inconsistencies between product_specialty_map and the actual bucket content in gcp
            product_directory = os.path.join(resources_directory, product)

            if hasattr(resources, product):
                setattr(resources, product, dict())
                product_obj = getattr(resources, product)
                
                for specialty_name in products_and_specialties[product]:
                    specialty_directory = os.path.join(product_directory, specialty_name)
                    product_obj[specialty_name] = specialty()

                    specialty_obj: specialty = product_obj[specialty_name]

                    try:
                        specialty_obj.ans_ref_system_prompt = load_text_file(os.path.join(specialty_directory, 'ans_ref_sys_prompt.txt'))
                    except Exception as e:
                        print(f"Error loading ans_ref_system_prompt for {specialty_name}: {e}")
                        specialty_obj.ans_ref_system_prompt = None
                        log_error( Error (
                                module="GCP_Resources_Download",
                                code=1011,
                                description="Error while downloading file",
                                excpetion=e
                        ), Severity.ERROR)

                    try:
                        specialty_obj.ans_ref_usr_prompt = load_text_file(os.path.join(specialty_directory, 'ans_ref_usr_prompt.txt'))
                    except Exception as e:
                        print(f"Error loading ans_ref_usr_prompt for {specialty_name}: {e}")
                        specialty_obj.ans_ref_usr_prompt = None
                        log_error( Error (
                                module="GCP_Resources_Download",
                                code=1012,
                                description="Error while downloading file",
                                excpetion=e
                        ), Severity.ERROR)

                    try:
                        specialty_obj.follow_up_system_prompt = load_text_file(os.path.join(specialty_directory, 'follow_up_sys_prompt.txt'))
                    except Exception as e:
                        print(f"Error loading follow_up_system_prompt for {specialty_name}: {e}")
                        specialty_obj.follow_up_system_prompt = None
                        log_error( Error (
                                module="GCP_Resources_Download",
                                code=1013,
                                description="Error while downloading file",
                                excpetion=e
                        ), Severity.ERROR)

                    try:
                        specialty_obj.knowledge = load_text_file(os.path.join(specialty_directory, 'knowledge.txt'))
                    except Exception as e:
                        print(f"Error loading knowledge for {specialty_name}: {e}")
                        specialty_obj.knowledge = None
                        log_error( Error (
                                module="GCP_Resources_Download",
                                code=1014,
                                description="Error while downloading file",
                                excpetion=e
                        ), Severity.ERROR)

                    try:
                        with open(os.path.join(specialty_directory, 'pre_def_response.json'), 'r') as file:
                            specialty_obj.pre_def_response = json.load(file)
                    except Exception as e:
                        print(f"Error loading pre_def_response for {specialty_name}: {e}")
                        specialty_obj.pre_def_response = None
                        log_error( Error (
                                module="GCP_Resources_Download",
                                code=1015,
                                description="Error while downloading file",
                                excpetion=e
                        ), Severity.ERROR)
            else:
                print(f"Product {product} does not exist in global_resources.")

    except Exception as e:
        print(f"Error while downloading GCP resources: {e}")
        log_error( Error (
                module="GCP_Resources_Download",
                code=1015,
                description="Error while downloading file",
                excpetion=e
        ), Severity.ERROR)

    finally:
        # delete ../gcp_download/
        shutil.rmtree(resources_directory)

    return resources