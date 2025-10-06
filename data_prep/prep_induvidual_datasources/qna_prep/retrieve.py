import requests
import html2text
import json
import os
from textwrap import dedent

class Document:
    def __init__(self, slug: str = "", content: str = ""):
        self.slug = slug
        self.content = content

    def to_dict(self):
        return {
            "slug": self.slug,
            "content": self.content
        }

def apply_tabs_to_text(text, num_tabs):
    lines = text.split('\n')
    tabbed_lines = [('\t' * num_tabs) + line for line in lines]
    return '\n'.join(tabbed_lines)
    
# set up induvidual QnAs directory
if not os.path.exists("./formatted_qna"):
    os.makedirs("./formatted_qna")
    print(f"Directory formatted_qna created.")
else:
    print(f"Directory formatted_qna already exists.")


# Set up the URL and the token
with open('./input_slugs.txt', 'r') as file:
    slugs = [line.strip() for line in file]
    
"""
Original code used a hard‑coded internal dev endpoint on the icliniq domain:
    https://dev-directus-gcp.icliniq.com/items/qa?...&filter={"slug": {"_eq": "<slug>"}}

We remove specific internal domains. Configure your own Directus (or similar) base URL(s) below.

INSTRUCTIONS:
1. Set QNA_API_BASE_DEV / QNA_API_BASE_PROD via environment variables or edit defaults.
2. Choose which environment to use with USE_QNA_DEV / USE_QNA_PROD.
3. Adjust FIELDS or FILTER_FIELD if your schema differs.
"""

QNA_API_BASE_DEV = os.environ.get("QNA_API_BASE_DEV", "<SET_QNA_DEV_BASE_URL>")
QNA_API_BASE_PROD = os.environ.get("QNA_API_BASE_PROD", "<SET_QNA_PROD_BASE_URL>")

USE_QNA_DEV = True
USE_QNA_PROD = False

if USE_QNA_DEV and USE_QNA_PROD:
    raise ValueError("Only one of USE_QNA_DEV or USE_QNA_PROD can be True.")
if not USE_QNA_DEV and not USE_QNA_PROD:
    raise ValueError("One of USE_QNA_DEV or USE_QNA_PROD must be True.")

FILTER_FIELD = "slug"
FIELDS = "title,titleMeta,slug,questionAnswer"
BASE_QNA_URL = QNA_API_BASE_DEV if USE_QNA_DEV else QNA_API_BASE_PROD

request_urls = []
for _ in slugs:
    request_urls.append(
        f"{BASE_QNA_URL}/items/qa?fields={FIELDS}&filter={{\"{FILTER_FIELD}\": {{\"_eq\": \"{_}\"}}}}"
    )
with open("./directus_token.txt", "r") as f:
    token = f.readline().strip()

# create all the qna objects in the required format

# get the text maker object ready
text_maker = html2text.HTML2Text()
text_maker.bypass_tables = False
text_maker.ignore_links = True

for url in request_urls:

    # (req, res)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)

    # clean and format res
    for _ in data:
        # print(_.keys())
        questionAnswers = _["questionAnswer"]["questionAnswers"]
        content = dedent('''
            Conversation between doctor and patient:
        ''').strip("\n")       
        for idx, questionAnswer in enumerate(questionAnswers):
            questionhtml, answerhtml = questionAnswer["question"], questionAnswer["answer"]
            questiontext, answertext = map(lambda x: text_maker.handle(x), [questionhtml, answerhtml])
            # print(questiontext, "\n\n\n", answertext)

            content += dedent(f'''
                              

    patient's question {idx + 1}:
    {apply_tabs_to_text(questiontext, 1)}
    
    doctor's answer to question {idx + 1}:
    {apply_tabs_to_text(answertext, 1)}
            ''').rstrip("\n")


        slug = _["slug"]
        # print(content)

        article_struct = Document(
            slug = slug,
            content = content
        )

        with open(f"./formatted_qna/{slug}.json", "w") as file:
            file.write(json.dumps(article_struct.to_dict(), indent=4))