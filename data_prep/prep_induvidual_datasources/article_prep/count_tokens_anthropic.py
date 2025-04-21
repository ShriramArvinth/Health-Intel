import anthropic
from pathlib import Path

# Initialize the client with your API key
# Load the API key from the file
api_key_path = Path(__file__).resolve().parent.parent.parent.parent / "app" / "secrets" / "anthropic_key.txt"
with open(api_key_path, "r") as f:
    api_key = f.readline().strip()

# Initialize the client with the API key
client = anthropic.Anthropic(api_key=api_key)

# Read the content of the XML file
with open('combined_articles.xml', 'r') as file:
    xml_content = file.read()

# Prepare the request with model, tools (if needed), and messages
response = client.messages.count_tokens(
    model="claude-3-7-sonnet-latest",
    messages=[{
        "role": "user",
        "content": xml_content
    }]
)

# Print the response
print(response.json())
