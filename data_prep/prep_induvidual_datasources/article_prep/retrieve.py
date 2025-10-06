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
if os.path.exists("./formatted_articles"):
    for filename in os.listdir("./formatted_articles"):
        file_path = os.path.join("./formatted_articles", filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            os.rmdir(file_path)
    print(f"Directory formatted_articles cleared.")
else:
    os.makedirs("./formatted_articles")
    print(f"Directory formatted_articles created.")


# Set up the URL and the token
with open('./input_slugs.txt', 'r') as file:
    slugs = [line.strip() for line in file]

"""
The original code contained hard-coded internal API endpoints on the icliniq domain, e.g.:
    https://dev-directus-gcp.icliniq.com/items/article?... (dev)
    https://content-platform.icliniq.com/items/article?... (prod)

Per migration/anonymization requirements, we avoid committing concrete internal URLs.

INSTRUCTIONS:
1. Set ARTICLE_API_BASE_DEV to your development Directus (or equivalent) base URL.
2. Set ARTICLE_API_BASE_PROD to your production Directus (or equivalent) base URL.
3. Exactly one of USE_DEV / USE_PROD should be True. (Both False raises an error.)
4. The request path/query pattern below matches the former API; adjust if your schema differs.

Expected pattern (example):
  {BASE}/items/article?fields=title,body,slug&filter={"urlPath": {"_eq": "<slug>"}}

If your API filters by a different field (e.g. slug instead of urlPath), update QUERY_FILTER_FIELD.
"""

ARTICLE_API_BASE_DEV = os.environ.get("ARTICLE_API_BASE_DEV", "<SET_DEV_BASE_URL>")  # e.g. https://dev-your-domain.example.com
ARTICLE_API_BASE_PROD = os.environ.get("ARTICLE_API_BASE_PROD", "<SET_PROD_BASE_URL>")  # e.g. https://prod-your-domain.example.com

# Toggle which environment to use.
USE_DEV = False
USE_PROD = True

QUERY_FILTER_FIELD = "urlPath"  # change to "slug" or another field if needed

if USE_DEV and USE_PROD:
    raise ValueError("Only one of USE_DEV or USE_PROD can be True.")
if not USE_DEV and not USE_PROD:
    raise ValueError("One of USE_DEV or USE_PROD must be True.")

BASE_URL = ARTICLE_API_BASE_DEV if USE_DEV else ARTICLE_API_BASE_PROD

request_urls = []
for _ in slugs:
    # Build the query dynamically without exposing previous internal domains.
    request_urls.append(
        f"{BASE_URL}/items/article?fields=title,body,slug&filter={{\"{QUERY_FILTER_FIELD}\": {{\"_eq\": \"{_}\"}}}}"
    )

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
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"Request failed for slug: {url}")
        print(e)
        continue
    if response.status_code == 200:
        data = response.json()["data"]
        print(data)
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