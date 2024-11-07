from anthropic import Anthropic
from pathlib import Path
import sys

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