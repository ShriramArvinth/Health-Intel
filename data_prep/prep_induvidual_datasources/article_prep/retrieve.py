import requests
import html2text
import json
import os

class Document:
    def __init__(self, slug: str = "", content: str = ""):
        self.slug = slug
        self.content = content

    def to_dict(self):
        return {
            "slug": self.slug,
            "content": self.content
        }

# set up induvidual articles directory
if not os.path.exists("./formatted_articles"):
    os.makedirs("./formatted_articles")
    print(f"Directory formatted_articles created.")
else:
    print(f"Directory formatted_articles already exists.")


# Set up the URL and the token
with open('./input_slugs.txt', 'r') as file:
    slugs = [line.strip() for line in file]

request_urls = []
for _ in slugs:
    # for dev
    # request_urls.append("https://dev-directus-gcp.icliniq.com/items/article?fields=title,body,slug&filter={\"slug\": {\"_eq\": \"" + _ + "\"}}") 

    # for prod
    request_urls.append("https://content-platform.icliniq.com/items/article?fields=title,body,slug&filter={\"slug\": {\"_eq\": \"" + _ + "\"}}")

    # for graphql prod
    # request_urls.append("https://content-platform.icliniq.com/items/article?fields=title,body,slug&filter={\"slug\": {\"_eq\": \"" + _ + "\"}}") 

with open("./directus_token.txt", "r") as f:
    lines = [line.strip() for line in f]
    # 2nd line is for prod directus bearer token
    token = lines[1]

# create all the article files in the required format
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
        print(_.keys())
        html_content = _["body"]
        text_maker = html2text.HTML2Text()
        text_maker.bypass_tables = False
        text_maker.ignore_links = True
        text = text_maker.handle(html_content)
        # print(text)
        slug = _["slug"]

        article_struct = Document(
            slug = slug,
            content = text
        )

        with open(f"./formatted_articles/{slug}.json", "w") as file:
            file.write(json.dumps(article_struct.to_dict()))