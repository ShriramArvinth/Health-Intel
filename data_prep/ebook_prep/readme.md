## What does this folder do?
inside `./retrieve_ebook/google_docs_extract_data.ipynb` there are scripts to pull the ebook from GCS, take out only the textual content from it, if there are tables in the textual content, convert them into markdown, and provide everything in a `./retrieve_ebook/google_docs_extract_data.txt`. This file is then renamed to `"<<specialty name>> Unmapped.txt"` and passed on to the medical team. The medical team returns with the mapping between the ebook and the articles by modifying the file given to them. This file returned by the medical team is renamed to `"<<specialty name>> Mapped.txt"`. The content in this `.txt` file is split on the basis of chapters (they are `[Section 1, Section 2, ...]`) by `ebook_to_xml.py` and stored inside `ebook1.xml` in this XML format: 

```
<all chapters>
	<chapter>	
	chapter 1 content
	</chapter>
	<chapter>	
	chapter 2 content
	</chapter>
</all chapters>
```
Since `ebook1.xml` contains `utf-8` characters, it can be read normally in Python code just like how it reads a text file.

If there is a necessity to split each section (chapter) in `"<<specialty name>> Mapped.txt"` into further subsections, make use of `subsection_split.py` which will do so and output its result inside `subsection_ebook.json`