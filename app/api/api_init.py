from dataclasses import dataclass
from anthropic import Anthropic
from pathlib import Path
import sys
from google.cloud.storage import Client, transfer_manager
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
        self.wld: specialty
        self.t1d: specialty

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
    bucket_name = "ai_chat_tes_resources"

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

def get_global_resources():
    resources_directory = get_gcp_resources()
    resources = global_resources()

    # Load chat_title and follow_up
    resources.chat_title = load_text_file(os.path.join(resources_directory, 'chat_title.txt'))
    specialties = [
        'wld',
        't1d',
        'gerd',
        'empower_az_demo',
        'psoriasis',
        'empower_atopic_dermatitis'
    ]

    # Loop through each specialty to load data
    for specialty_name in specialties:
        specialty_directory = os.path.join(resources_directory, specialty_name)

        setattr(resources, specialty_name, specialty())
        specialty_obj: specialty = getattr(resources, specialty_name)

        try:
            specialty_obj.ans_ref_system_prompt = load_text_file(os.path.join(specialty_directory, 'ans_ref_sys_prompt.txt'))
        except Exception as e:
            print(f"Error loading ans_ref_system_prompt for {specialty_name}: {e}")
            specialty_obj.ans_ref_system_prompt = None

        try:
            specialty_obj.ans_ref_usr_prompt = load_text_file(os.path.join(specialty_directory, 'ans_ref_usr_prompt.txt'))
        except Exception as e:
            print(f"Error loading ans_ref_usr_prompt for {specialty_name}: {e}")
            specialty_obj.ans_ref_usr_prompt = None

        try:
            specialty_obj.follow_up_system_prompt = load_text_file(os.path.join(specialty_directory, 'follow_up_sys_prompt.txt'))
        except Exception as e:
            print(f"Error loading follow_up_system_prompt for {specialty_name}: {e}")
            specialty_obj.follow_up_system_prompt = None

        try:
            specialty_obj.knowledge = load_text_file(os.path.join(specialty_directory, 'knowledge.txt'))
        except Exception as e:
            print(f"Error loading knowledge for {specialty_name}: {e}")
            specialty_obj.knowledge = None

        try:
            with open(os.path.join(specialty_directory, 'pre_def_response.json'), 'r') as file:
                specialty_obj.pre_def_response = json.load(file)
        except Exception as e:
            print(f"Error loading pre_def_response for {specialty_name}: {e}")
            specialty_obj.pre_def_response = None

    # delete ../gcp_download/
    shutil.rmtree(resources_directory)

    return resources