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

directory_path = "./formatted_qna/"
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

def item_func(x):
    return (x.split("_")[-1])
combined_xml = dicttoxml2.dicttoxml(
    obj = combined_articles.to_dict(), 
    root = False, 
    attr_type = False,
    item_func = item_func
)

proper_string = str(html.unescape(combined_xml.decode('utf-8', errors="ignore")))
fragment = etree.fromstring(proper_string)
etree.strip_tags(fragment,'item_name_article')
xml_tree_string = etree.tostring(fragment, pretty_print = True)
with open("./combined_qna.xml", "w") as file:
    file.write(html.unescape(xml_tree_string.decode('utf-8', errors="ignore")))

# dom = parseString(combined_xml)
# with open("combined_qna.xml", "w") as file:
    # file.write(html.unescape(combined_xml.decode('utf-8', errors="ignore")))
    # file.write(dom.toprettyxml())
    # file.write(str(combined_xml))