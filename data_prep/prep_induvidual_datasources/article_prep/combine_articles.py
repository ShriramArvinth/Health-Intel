from typing import List
import json
import os
import dicttoxml2
from xml.dom.minidom import parseString
import html
from lxml import etree


class Document:
    def __init__(self, slug: str = "", content: str = ""):
        self.slug = slug
        self.content = content

    def to_dict(self):
        return {
            "slug": self.slug,
            "content": self.content
        }

class JSONArticleTemplate:
    def __init__(self, all_articles: List[Document]):
        self.all_articles = all_articles

    def to_dict(self):
        return {
            "all_articles": {
                "item_name_article": [document.to_dict() for document in self.all_articles]
            }
        }


directory_path = "./formatted_articles/"
article_paths = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file))]


combined_articles = JSONArticleTemplate(
    all_articles = []
)
for _ in article_paths:
    file_path = _
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        combined_articles.all_articles.append(
            Document(
                slug = data["slug"],
                content = data["content"]
            )
        )

output_file = "knowledge.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("<all-articles>\n")
    for doc in combined_articles.all_articles:
        f.write("  <article>\n")
        f.write("    <slug>{}</slug>\n".format(doc.slug))
        f.write("    <content>{}</content>\n".format(doc.content))
        f.write("  </article>\n")
    f.write("</all-articles>\n")

print(f"Formatted XML saved to {output_file}")


