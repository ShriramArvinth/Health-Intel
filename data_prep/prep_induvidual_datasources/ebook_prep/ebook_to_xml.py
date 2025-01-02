import re
from typing import List
import dicttoxml2
import html
import json
from lxml import etree

class Document:
    def __init__(self, content: str = ""):
        self.content = content

    def to_dict(self):
        return {
            "content": self.content
        }

class JSONEbookTemplate:
    def __init__(self, all_chapters: List[Document]):
        self.all_chapters = all_chapters

    def to_dict(self):
        return {
            "all_chapters": {
                "item_name_chapter": [document.to_dict() for document in self.all_chapters]
            }
        }

file_path = './knowledge.txt'
with open(file_path, 'r') as file:
    content = file.read()

# remove >, < with text, as it will throw erros when converted to XML
content = re.sub(r"<", "less than", content)
content = re.sub(r">", "greater than", content)

ebook = JSONEbookTemplate(
    all_chapters = []
)

for section_match in re.finditer(r'((?:^Section \d+.*?(?=^Section \d+|\Z))|(?:^.+?(?=^Section \d+|\Z)))', content, re.MULTILINE | re.DOTALL):
    ebook.all_chapters.append(
        Document(
            content = section_match.group()
        )
    )

# with open(f"./ebook.json", "w") as file:
#     file.write(json.dumps(ebook.to_dict()))

def item_func(x):
    return (x.split("_")[-1])
ebook_xml = dicttoxml2.dicttoxml(
    obj = ebook.to_dict(), 
    root = False, 
    attr_type = False,
    item_func = item_func
)

# xml to proper string from a bytes object
    # html.unescape converts elements that are unknown to utf-8 to their proper string format in unicode
proper_string = str(html.unescape(ebook_xml.decode('utf-8', errors="ignore")))

# # write uncleaned xml to file
# with open("./ebook1.xml", "w") as file:
#      file.write(proper_string)

# cleaning the XML string
fragment = etree.fromstring(proper_string)
etree.strip_tags(fragment,'item_name_chapter')
xml_tree_string = etree.tostring(fragment, pretty_print = True)

# write to file in proper utf-8 characters
with open("./ebook1.xml", "w") as file:
     file.write(html.unescape(xml_tree_string.decode('utf-8', errors="ignore")))