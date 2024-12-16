import re
from typing import List
import json

class Subsection:
    def __init__(self, content: str = ""):
        self.content = content

    def to_dict(self):
        return {
            "content": self.content
        }

class Document:
    def __init__(self, title: str, all_subsections: List[Subsection]):
        self.all_subsections = all_subsections
        self.section_title = title

    def to_dict(self):
        return {
            "section title": self.section_title,
            "item_name_subsection": [subsection.to_dict() for subsection in self.all_subsections]
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
    
file_path = './T1D Mapped.txt'
with open(file_path, 'r') as file:
    content = file.read()

ebook = JSONEbookTemplate(
    all_chapters = []
)

for section_match in re.finditer(r'(Section \d+.*?)(?=Section \d+|$)', content, re.DOTALL):
    section = Document(
        title = "",
        all_subsections = []
    )

    for idx, subsection_match in enumerate(re.finditer(r'^(Section \d+ - .*?)(?=(\n\d+\.\d+)|$)|^(\d+\.\d+ .*\n(?:.*?(?=\n\d+\.\d+|$)))', section_match.group(), re.DOTALL | re.MULTILINE), 1):
        
        if idx == 1:
            section.section_title = subsection_match.group()
        
        else:
            section.all_subsections.append(
                Subsection(
                    content = subsection_match.group()
                )
            )
    # section.all_subsections.append(
    #     Subsection(
    #         content = section_match.group()
    #     )
    # )
    ebook.all_chapters.append(
        section
    )

with open(f"./subsection_ebook.json", "w") as file:
    file.write(json.dumps(ebook.to_dict()))