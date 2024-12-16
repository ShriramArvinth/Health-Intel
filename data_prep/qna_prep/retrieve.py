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
slugs = [
    "i-am-planing-to-go-for-liposuction-for-weight-loss-my-weight-is-78kgs",
    "what-can-be-the-reason-for-my-frequent-hunger-and-weight-loss"
]
request_urls = []
for _ in slugs:
    request_urls.append("https://dev-directus-gcp.icliniq.com/items/qa?fields=title,titleMeta,slug,questionAnswer&filter={\"slug\": {\"_eq\": \"" + _ + "\"}}")
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